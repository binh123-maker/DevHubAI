from uuid import UUID, uuid4
import re
from app.models.document import DocumentStructureNode
from app.services.processors.base import ExtractedDocument

def parse_structure(document_version_id: UUID, extracted: ExtractedDocument) -> list[DocumentStructureNode]:
    nodes: list[DocumentStructureNode] = []
    
    # Track hierarchy using a stack or list of last headings
    # active_headings[level] = node_id
    active_headings: dict[int, UUID] = {}
    last_node_id: UUID | None = None
    
    global_char_offset = 0
    global_line_offset = 0
    order_index = 0

    for page in extracted.pages:
        md_text = page.markdown if hasattr(page, 'markdown') else page.raw_text
        
        # Split markdown text into paragraph/block items
        blocks = re.split(r'\n\n+', md_text)
        
        for block in blocks:
            block = block.strip()
            if not block:
                continue
                
            block_lines = block.splitlines()
            line_count = len(block_lines)
            char_len = len(block)
            
            char_start = global_char_offset
            char_end = global_char_offset + char_len
            line_start = global_line_offset + 1
            line_end = global_line_offset + line_count
            
            # 1. Determine Node Category and Type
            node_category = "layout"
            node_type = "paragraph"
            hierarchy_level = 0
            language = None
            metadata_json = {}
            
            # Heading check
            if block.startswith('#'):
                m = re.match(r'^(#+)\s*(.*)', block)
                if m:
                    level = len(m.group(1))
                    node_category = "layout"
                    node_type = "heading"
                    hierarchy_level = level
                    metadata_json = {"heading_text": m.group(2)}
            # Code block check
            elif block.startswith('```'):
                node_category = "code"
                node_type = "code_block"
                m = re.match(r'^```(\w*)', block)
                if m:
                    language = m.group(1) or None
            # List check
            elif block.startswith(('-', '*', '+')) or re.match(r'^\d+\.', block):
                node_category = "layout"
                node_type = "list"
            # Table check
            elif '|' in block and '-' in block:
                node_category = "layout"
                node_type = "table"
                
            # 2. Determine Parent ID based on hierarchy
            node_id = uuid4()
            parent_id = None
            
            if node_type == "heading":
                # Find the nearest higher-level heading (lower level number)
                parent_level = hierarchy_level - 1
                while parent_level > 0:
                    if parent_level in active_headings:
                        parent_id = active_headings[parent_level]
                        break
                    parent_level -= 1
                # Update active headings
                active_headings[hierarchy_level] = node_id
                # Remove deeper headings from active stack
                levels_to_remove = [l for l in active_headings if l > hierarchy_level]
                for l in levels_to_remove:
                    active_headings.pop(l, None)
            else:
                # Parent is the deepest active heading
                if active_headings:
                    max_level = max(active_headings.keys())
                    parent_id = active_headings[max_level]
            
            # Create node object
            node = DocumentStructureNode(
                id=node_id,
                document_version_id=document_version_id,
                node_category=node_category,
                node_type=node_type,
                parent_id=parent_id,
                order_index=order_index,
                hierarchy_level=hierarchy_level,
                page_start=page.page_number,
                page_end=page.page_number,
                char_start=char_start,
                char_end=char_end,
                line_start=line_start,
                line_end=line_end,
                language=language,
                content_text=block,
                content_markdown=block,
                metadata_json=metadata_json
            )
            nodes.append(node)
            
            order_index += 1
            global_char_offset += char_len + 2  # account for split spacing
            global_line_offset += line_count + 1

    return nodes
