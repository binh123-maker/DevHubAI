from uuid import UUID
import hashlib
from app.models.document import DocumentStructureNode
from app.services.chunker import _split_into_sentences

MAX_CHARS = 1500

def build_chunks_from_structure(nodes: list[DocumentStructureNode]) -> list[dict]:
    chunks = []
    chunk_index = 0

    for node in nodes:
        # Skip structural container nodes that have empty content
        if not node.content_text or not node.content_text.strip():
            continue
            
        # Do not index heading nodes separately as text chunks since they are metadata
        if node.node_type == "heading":
            continue

        content = node.content_text
        md_content = node.content_markdown
        
        # Split block if it exceeds MAX_CHARS
        if len(content) <= MAX_CHARS:
            parts = [(content, md_content)]
        else:
            sentences = _split_into_sentences(content)
            parts = []
            buf = ""
            for sent in sentences:
                if len(buf) + len(sent) > MAX_CHARS:
                    if buf:
                        parts.append((buf.strip(), buf.strip()))
                    buf = sent
                else:
                    buf = (buf + " " + sent).strip() if buf else sent
            if buf:
                parts.append((buf.strip(), buf.strip()))

        for part_text, part_md in parts:
            char_count = len(part_text)
            word_count = len(part_text.split())
            token_count = int(char_count / 4)
            chunk_hash = hashlib.sha256(part_text.encode('utf-8')).hexdigest()

            # Trace heading hierarchy
            heading = None
            parent = node
            visited = set()
            while parent and parent.id not in visited:
                visited.add(parent.id)
                if parent.node_type == "heading":
                    heading = parent.content_text.lstrip('#').strip()
                    break
                if parent.parent_id:
                    parent = next((n for n in nodes if n.id == parent.parent_id), None)
                else:
                    parent = None

            chunks.append({
                "structure_node_id": node.id,
                "chunk_index": chunk_index,
                "content": part_text,
                "content_markdown": part_md,
                "page_number": node.page_start,
                "line_start": node.line_start,
                "line_end": node.line_end,
                "char_start": node.char_start,
                "char_end": node.char_end,
                "token_count": token_count,
                "char_count": char_count,
                "word_count": word_count,
                "hash": chunk_hash,
                "heading": heading,
            })
            chunk_index += 1

    return chunks
