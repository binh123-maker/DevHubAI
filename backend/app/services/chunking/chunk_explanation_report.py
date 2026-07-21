import json
from typing import List, Dict, Any, Optional

class ChunkExplanationReport:
    def __init__(self, items: List[Dict[str, Any]], stats: Optional[Dict[str, Any]] = None):
        self.items = items
        self.stats = stats or {}

    def to_json(self) -> str:
        return json.dumps({
            "items": self.items,
            "statistics": self.stats
        }, indent=2, default=str)

    def to_markdown(self) -> str:
        lines = [
            "# Chunk Production & Explanation Report",
            "",
            "## Production Summaries",
            "",
            "| Chunk ID | Signature | Quality Score | Retrieval Weight | Dominant Type | Search Modes | Heading Path |",
            "|---|---|---|---|---|---|---|",
        ]
        for item in self.items:
            modes = ", ".join(item.get("recommended_search_modes", []))
            hpath = " / ".join(item.get("heading_path", []))
            lines.append(
                f"| {item.get('id')} | {item.get('chunk_signature')} | {item.get('quality_score'):.2f} | "
                f"{item.get('retrieval_weight'):.2f} | {item.get('dominant_type')} | {modes} | {hpath} |"
            )
        
        # 10.3D extended reports
        lines.append("\n## Optimization & Validation Summary\n")
        lines.append(f"- Merge operations count: {self.stats.get('merge_count', 0)}")
        lines.append(f"- Split operations count: {self.stats.get('split_count', 0)}")
        lines.append(f"- Cache hit ratio: {self.stats.get('cache_statistics', {}).get('hit_ratio', 0.0):.2f}")
            
        return "\n".join(lines)

    def pretty_print(self) -> str:
        lines = ["=== Chunk Explanation & Production Report ==="]
        for item in self.items:
            lines.append(
                f"Chunk ID: {item.get('id')}\n"
                f"  Signature: {item.get('chunk_signature')}\n"
                f"  Type: {item.get('dominant_type')}\n"
                f"  Quality Breakdown: {item.get('quality_breakdown')}\n"
                f"  Search Modes: {item.get('recommended_search_modes')}"
            )
        return "\n".join(lines)

