import json
import uuid
from typing import List, Optional, Tuple, Dict, Any

class ChunkGraph:
    def __init__(self, chunks: List[Any]):
        self.chunks_list = chunks
        self.chunks = {c.id: c for c in chunks}
        self.chunk_by_index = {c.chunk_index: c for c in chunks}

    def previous(self, chunk: Any) -> Optional[Any]:
        return self.chunk_by_index.get(chunk.chunk_index - 1)

    def next(self, chunk: Any) -> Optional[Any]:
        return self.chunk_by_index.get(chunk.chunk_index + 1)

    def neighbors(self, chunk: Any) -> Tuple[Optional[Any], Optional[Any]]:
        return self.previous(chunk), self.next(chunk)

    def find_chunk(self, chunk_id: uuid.UUID) -> Optional[Any]:
        return self.chunks.get(chunk_id)

    # 10.3D extended navigations
    def find_previous(self, chunk: Any) -> Optional[Any]:
        return self.previous(chunk)

    def find_next(self, chunk: Any) -> Optional[Any]:
        return self.next(chunk)

    def find_neighbors(self, chunk: Any) -> Tuple[Optional[Any], Optional[Any]]:
        return self.neighbors(chunk)

    def find_related(self, chunk: Any) -> List[Any]:
        # Related chunks sharing same heading path
        return [c for c in self.chunks_list if c.heading_path == chunk.heading_path and c.id != chunk.id]

    def find_subgraph(self, chunk_ids: List[uuid.UUID]) -> Dict[str, Any]:
        sub_chunks = [self.find_chunk(cid) for cid in chunk_ids if self.find_chunk(cid)]
        edges = []
        for sc in sub_chunks:
            nxt = self.next(sc)
            if nxt and nxt.id in chunk_ids:
                edges.append((str(sc.id), str(nxt.id)))
        return {
            "nodes": [sc.to_dict() for sc in sub_chunks],
            "edges": edges
        }

    def find_path(self, start_chunk_id: uuid.UUID, end_chunk_id: uuid.UUID) -> List[uuid.UUID]:
        start = self.find_chunk(start_chunk_id)
        end = self.find_chunk(end_chunk_id)
        if not start or not end:
            return []

        path = []
        curr = start
        visited = set()
        
        while curr and curr.id not in visited:
            path.append(curr.id)
            if curr.id == end.id:
                break
            visited.add(curr.id)
            curr = self.next(curr)

        return path

    def export_mermaid(self) -> str:
        lines = ["graph TD"]
        for c in self.chunks_list:
            snippet = c.content[:20].replace('"', '\\"') + "..."
            lines.append(f"  Chunk_{c.chunk_index}[\"Chunk {c.chunk_index} ({c.estimated_tokens} tokens): {snippet}\"]")
            nxt = self.next(c)
            if nxt:
                lines.append(f"  Chunk_{c.chunk_index} --> Chunk_{nxt.chunk_index}")
        return "\n".join(lines)

    def export_graphviz(self) -> str:
        lines = ["digraph G {", "  node [shape=box];"]
        for c in self.chunks_list:
            snippet = c.content[:20].replace('"', '\\"')
            lines.append(f"  \"chunk_{c.chunk_index}\" [label=\"Chunk {c.chunk_index}\\n{snippet}\"];")
            nxt = self.next(c)
            if nxt:
                lines.append(f"  \"chunk_{c.chunk_index}\" -> \"chunk_{nxt.chunk_index}\";")
        lines.append("}")
        return "\n".join(lines)

    def export_json(self) -> str:
        data = {
            "chunks": [c.to_dict() for c in self.chunks_list]
        }
        return json.dumps(data, indent=2, default=str)
