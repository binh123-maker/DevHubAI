from uuid import UUID, uuid4
from typing import Any
from app.services.document_structure.node_types import NodeType

class DocumentTreeBuilder:
    def __init__(self, document_version_id: UUID):
        self.document_version_id = document_version_id
        self.nodes: list[dict[str, Any]] = []
        self.order_index = 0
        # Tracks active heading nodes by hierarchy level
        self.active_headings: dict[int, UUID] = {}

    def add_node(
        self,
        node_type: NodeType,
        node_category: str,
        content_text: str,
        content_markdown: str,
        page_start: int,
        page_end: int,
        char_start: int,
        char_end: int,
        line_start: int,
        line_end: int,
        hierarchy_level: int = 0,
        language: str | None = None,
        metadata_json: dict | None = None
    ) -> UUID:
        node_id = uuid4()
        
        # Determine parent
        parent_id = None
        if node_type in (NodeType.HEADING_1, NodeType.HEADING_2, NodeType.HEADING_3, NodeType.HEADING_4, NodeType.HEADING_5, NodeType.HEADING_6):
            try:
                level = hierarchy_level or int(node_type.value.split("_")[1])
            except Exception:
                level = hierarchy_level or 1
            
            # Auto-repair skipped heading levels: find the closest active heading
            # that has a level strictly less than 'level'
            closest_level = -1
            for active_lvl in self.active_headings.keys():
                if active_lvl < level and active_lvl > closest_level:
                    closest_level = active_lvl
                    
            if closest_level != -1:
                parent_id = self.active_headings[closest_level]
                # If level is skipped (e.g. active level 1, current level 3),
                # we repair the hierarchy_level of this node to be closest_level + 1
                if level > closest_level + 1:
                    level = closest_level + 1
            else:
                # No smaller active level exists, must parent under top-level
                level = 1
                
            self.active_headings[level] = node_id
            
            # Evict deeper active headings
            deeper_levels = [l for l in list(self.active_headings.keys()) if l > level]
            for l in deeper_levels:
                self.active_headings.pop(l, None)
            hierarchy_level = level
        else:
            if self.active_headings:
                max_level = max(self.active_headings.keys())
                parent_id = self.active_headings[max_level]
                hierarchy_level = max_level + 1
            else:
                hierarchy_level = 0

        node = {
            "id": node_id,
            "document_version_id": self.document_version_id,
            "node_category": node_category,
            "node_type": node_type.value,
            "parent_id": parent_id,
            "order_index": self.order_index,
            "hierarchy_level": hierarchy_level,
            "page_start": page_start,
            "page_end": page_end,
            "char_start": char_start,
            "char_end": char_end,
            "line_start": line_start,
            "line_end": line_end,
            "language": language,
            "content_text": content_text,
            "content_markdown": content_markdown,
            "metadata_json": metadata_json or {}
        }
        
        self.nodes.append(node)
        self.order_index += 1
        return node_id

    def finalize(self) -> list[dict[str, Any]]:
        # Post-process the flat list of nodes to compute sibling ordering and section boundaries
        
        # 1. Compute sibling ordering
        from collections import defaultdict
        children_map = defaultdict(list)
        node_by_id = {node["id"]: node for node in self.nodes}
        
        for node in self.nodes:
            parent_id = node["parent_id"]
            children_map[parent_id].append(node["id"])
            
        for parent_id, child_ids in children_map.items():
            for idx, child_id in enumerate(child_ids):
                node_by_id[child_id]["metadata_json"]["sibling_index"] = idx
                
        # 2. Compute section boundaries for heading nodes
        heading_types = (
            NodeType.HEADING_1.value,
            NodeType.HEADING_2.value,
            NodeType.HEADING_3.value,
            NodeType.HEADING_4.value,
            NodeType.HEADING_5.value,
            NodeType.HEADING_6.value
        )
        
        for i, node in enumerate(self.nodes):
            if node["node_type"] in heading_types:
                curr_level = node["hierarchy_level"]
                
                section_char_end = node["char_end"]
                section_line_end = node["line_end"]
                section_page_end = node["page_end"]
                
                for j in range(i + 1, len(self.nodes)):
                    next_node = self.nodes[j]
                    if next_node["node_type"] in heading_types:
                        next_level = next_node["hierarchy_level"]
                        if next_level <= curr_level:
                            break
                    section_char_end = max(section_char_end, next_node["char_end"])
                    section_line_end = max(section_line_end, next_node["line_end"])
                    section_page_end = max(section_page_end, next_node["page_end"] or section_page_end)
                    
                node["metadata_json"]["section_boundary"] = {
                    "char_start": node["char_start"],
                    "char_end": section_char_end,
                    "line_start": node["line_start"],
                    "line_end": section_line_end,
                    "page_start": node["page_start"],
                    "page_end": section_page_end
                }

        # 3. Compute section boundaries for lists, tables, and code blocks
        idx = 0
        while idx < len(self.nodes):
            node = self.nodes[idx]
            if node["node_type"] in (NodeType.BULLET_LIST.value, NodeType.NUMBERED_LIST.value):
                # Group consecutive list items
                start_node = node
                end_node = node
                next_idx = idx + 1
                while next_idx < len(self.nodes) and self.nodes[next_idx]["node_type"] == node["node_type"]:
                    end_node = self.nodes[next_idx]
                    next_idx += 1
                
                boundary = {
                    "char_start": start_node["char_start"],
                    "char_end": end_node["char_end"],
                    "line_start": start_node["line_start"],
                    "line_end": end_node["line_end"],
                    "page_start": start_node["page_start"],
                    "page_end": end_node["page_end"]
                }
                
                for k in range(idx, next_idx):
                    self.nodes[k]["metadata_json"]["section_boundary"] = boundary
                idx = next_idx
            elif node["node_type"] in (NodeType.CODE_BLOCK.value, NodeType.TABLE.value):
                node["metadata_json"]["section_boundary"] = {
                    "char_start": node["char_start"],
                    "char_end": node["char_end"],
                    "line_start": node["line_start"],
                    "line_end": node["line_end"],
                    "page_start": node["page_start"],
                    "page_end": node["page_end"]
                }
                idx += 1
            else:
                idx += 1

        # 4. Compute structure metadata enrichment
        import re
        from app.services.metadata_builder import build_metadata
        for node in self.nodes:
            text = node["content_text"] or ""
            markdown = node["content_markdown"] or ""
            words = text.split()
            word_count = len(words)
            token_estimate = int(len(text) / 4) + 1
            
            # Sentence count
            sentences = re.split(r'[.!?]+', text)
            sentence_count = len([s for s in sentences if s.strip()])
            
            # Paragraph count
            paragraphs = [p for p in text.split("\n\n") if p.strip()]
            paragraph_count = len(paragraphs) if paragraphs else 1
            
            # Reading time (minutes)
            reading_time = round(word_count / 200, 3)
            
            # Boolean metadata flags
            node_type = node["node_type"]
            contains_code = node_type == NodeType.CODE_BLOCK.value or "```" in markdown or "`" in markdown
            contains_table = node_type == NodeType.TABLE.value or "|" in markdown
            contains_image = node_type == NodeType.IMAGE.value or "![" in markdown
            contains_formula = node_type == NodeType.FORMULA.value or "$$" in markdown or "$" in markdown
            contains_list = node_type in (NodeType.BULLET_LIST.value, NodeType.NUMBERED_LIST.value)
            
            # Paths resolution
            heading_path = []
            curr_parent_id = node["parent_id"]
            while curr_parent_id:
                p_node = node_by_id[curr_parent_id]
                if p_node["node_type"] in heading_types:
                    heading_path.append(p_node["content_text"])
                curr_parent_id = p_node["parent_id"]
            heading_path.reverse()
            
            # section_path is parent headings AND current node if current is heading
            section_path = list(heading_path)
            if node_type in heading_types:
                section_path.append(text)
                
            # Get keywords and other metadata using the metadata_builder service
            old_meta = build_metadata(text, contains_code, node["language"])
            
            # Merge existing metadata_json keys
            merged_meta = dict(node.get("metadata_json", {}))
            merged_meta.update(old_meta)
            
            # Guarantee default keywords key is present
            if "keywords" not in merged_meta:
                merged_meta["keywords"] = []
            
            merged_meta.update({
                "word_count": word_count,
                "token_estimate": token_estimate,
                "sentence_count": sentence_count,
                "paragraph_count": paragraph_count,
                "reading_time": reading_time,
                "contains_code": contains_code,
                "contains_table": contains_table,
                "contains_image": contains_image,
                "contains_formula": contains_formula,
                "contains_list": contains_list,
                "language": node["language"] or "en",
                "heading_path": heading_path,
                "document_path": heading_path,
                "section_path": section_path
            })
            
            # If node is a heading, store heading_level
            if node_type in heading_types:
                merged_meta["heading_level"] = node["hierarchy_level"]
                
            node["metadata_json"] = merged_meta
                
        return self.nodes
