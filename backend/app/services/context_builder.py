from typing import Any
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.document import DocumentChunk, DocumentStructureNode
from app.schemas.search import SearchResult

class ContextBuilder:
    def __init__(self, token_budget: int = 4000):
        self.token_budget = token_budget

    def build_context(self, db: Session, search_results: list[SearchResult]) -> tuple[str, list[dict]]:
        """
        Builds optimized grounded context.
        1. Deduplicate chunks.
        2. Merge adjacent chunks (consecutive chunk_index for same document).
        3. Expand context hierarchy using heading trails/parents.
        4. Split into sections (Code vs. Natural Language).
        5. Trim context based on token budget.
        6. Return formatted context string and citation mapping list.
        """
        if not search_results:
            return "", []

        # 1. Deduplicate by chunk_id
        unique_results = []
        seen = set()
        for res in search_results:
            if res.chunk_id not in seen:
                seen.add(res.chunk_id)
                unique_results.append(res)

        # Sort by document_id and then chunk_index to make merging easier
        unique_results.sort(key=lambda x: (x.document_id, x.chunk_index if x.chunk_index is not None else 0))

        # 2. Merge adjacent chunks
        merged_chunks = []
        for res in unique_results:
            if not merged_chunks:
                merged_chunks.append({
                    "document_id": res.document_id,
                    "document_name": res.document_name,
                    "source_url": res.source_url,
                    "heading": res.heading,
                    "chunk_indices": [res.chunk_index],
                    "content": res.content,
                    "relevance_score": res.relevance_score,
                    "line_start": res.line_start,
                    "line_end": res.line_end,
                    "page_number": res.page_number,
                    "chunk_ids": [res.chunk_id]
                })
            else:
                last = merged_chunks[-1]
                # If same document and adjacent chunk index, merge them
                if (last["document_id"] == res.document_id and 
                        res.chunk_index is not None and 
                        last["chunk_indices"][-1] is not None and 
                        res.chunk_index == last["chunk_indices"][-1] + 1):
                    last["chunk_indices"].append(res.chunk_index)
                    last["content"] += "\n" + res.content
                    last["line_end"] = res.line_end
                    last["relevance_score"] = max(last["relevance_score"], res.relevance_score)
                    last["chunk_ids"].append(res.chunk_id)
                else:
                    merged_chunks.append({
                        "document_id": res.document_id,
                        "document_name": res.document_name,
                        "source_url": res.source_url,
                        "heading": res.heading,
                        "chunk_indices": [res.chunk_index],
                        "content": res.content,
                        "relevance_score": res.relevance_score,
                        "line_start": res.line_start,
                        "line_end": res.line_end,
                        "page_number": res.page_number,
                        "chunk_ids": [res.chunk_id]
                    })

        # 3. Expand parent context/hierarchy
        # For each merged block, check if there's structure hierarchy in DB
        for block in merged_chunks:
            # Look up first chunk's structure node to find parent trail
            first_chunk_id = block["chunk_ids"][0]
            db_chunk = db.get(DocumentChunk, first_chunk_id)
            if db_chunk and db_chunk.structure_node_id:
                node = db.get(DocumentStructureNode, db_chunk.structure_node_id)
                if node and node.parent_id:
                    # Find parent headings
                    trail = []
                    curr = db.get(DocumentStructureNode, node.parent_id)
                    visited = set()
                    while curr and curr.id not in visited:
                        visited.add(curr.id)
                        if curr.node_type == "heading":
                            trail.append(curr.content_text.lstrip('#').strip())
                        if curr.parent_id:
                            curr = db.get(DocumentStructureNode, curr.parent_id)
                        else:
                            break
                    if trail:
                        block["heading"] = " > ".join(reversed(trail))

        # Sort back by relevance score descending
        merged_chunks.sort(key=lambda x: x["relevance_score"], reverse=True)

        # 4. Separate into sections (Code vs. Natural Language) and format
        code_blocks = []
        text_blocks = []
        
        for block in merged_chunks:
            is_code = block["content"].strip().startswith("```") or "def " in block["content"] or "class " in block["content"]
            if is_code:
                code_blocks.append(block)
            else:
                text_blocks.append(block)

        # 5. Enforce Token Budget
        selected_code = []
        selected_text = []
        current_token_count = 0

        # Iterate through code then text or vice versa. Let's do higher relevance first!
        all_selected = []
        combined_blocks = sorted(code_blocks + text_blocks, key=lambda x: x["relevance_score"], reverse=True)
        
        for block in combined_blocks:
            # Estimate tokens: ~4 chars per token
            est_tokens = len(block["content"]) // 4
            if current_token_count + est_tokens <= self.token_budget:
                all_selected.append(block)
                current_token_count += est_tokens
            else:
                continue

        # Group by code vs text for section separation
        final_code = [b for b in all_selected if b in code_blocks]
        final_text = [b for b in all_selected if b in text_blocks]

        # 6. Build the formatted context string
        context_parts = []
        if final_code:
            context_parts.append("=== CODE CONTEXT ===")
            for idx, b in enumerate(final_code):
                header = f"[Code Citation #{idx+1}] Document: {b['document_name']} | Path/Heading: {b['heading'] or 'None'}"
                context_parts.append(f"{header}\n{b['content']}")

        if final_text:
            context_parts.append("=== NATURAL LANGUAGE CONTEXT ===")
            for idx, b in enumerate(final_text):
                citation_num = len(final_code) + idx + 1
                header = f"[Text Citation #{citation_num}] Document: {b['document_name']} | Section: {b['heading'] or 'General'}"
                context_parts.append(f"{header}\n{b['content']}")

        context_string = "\n\n--------------------------------\n\n".join(context_parts)

        # Build citation mappings (clean lists of sources for response citations)
        citations_mapping = []
        citation_idx = 1
        for b in final_code:
            for cid in b["chunk_ids"]:
                citations_mapping.append({
                    "citation_number": citation_idx,
                    "chunk_id": cid,
                    "document_name": b["document_name"],
                    "source_url": b["source_url"]
                })
            citation_idx += 1
        for b in final_text:
            for cid in b["chunk_ids"]:
                citations_mapping.append({
                    "citation_number": citation_idx,
                    "chunk_id": cid,
                    "document_name": b["document_name"],
                    "source_url": b["source_url"]
                })
            citation_idx += 1

        return context_string, citations_mapping
