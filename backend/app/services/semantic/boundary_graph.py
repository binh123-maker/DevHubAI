import uuid
import json
from typing import Dict, List, Optional, Tuple, Any

class BoundaryExplanationReport:
    def __init__(self, items: List[Dict[str, Any]]):
        self.items = items

    def to_json(self) -> str:
        return json.dumps(self.items, indent=2, default=str)

    def to_markdown(self) -> str:
        lines = [
            "# Boundary Explanation Report",
            "",
            "| Boundary ID | Type | Matches | Rejections | Confidence | Quality | Recommendation | Reason |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for item in self.items:
            matched = ", ".join(item.get("matched_rules", []))
            rejected = ", ".join(item.get("rejected_rules", []))
            lines.append(
                f"| {item.get('id')} | {item.get('type')} | {matched} | {rejected} | "
                f"{item.get('confidence'):.2f} | {item.get('quality'):.2f} | {item.get('recommendation')} | "
                f"{item.get('reason')} |"
            )
        return "\n".join(lines)

    def pretty_print(self) -> str:
        lines = ["=== Boundary Explanation Report ==="]
        for item in self.items:
            lines.append(
                f"ID: {item.get('id')} ({item.get('type')})\n"
                f"  Matched: {item.get('matched_rules')}\n"
                f"  Confidence: {item.get('confidence'):.2f} | Quality: {item.get('quality'):.2f}\n"
                f"  Recommendation: {item.get('recommendation')}\n"
                f"  Reason: {item.get('reason')}"
            )
        return "\n".join(lines)


class BoundaryGraph:
    def __init__(self, units: List[Any], boundaries: List[Any]):
        self.units_list = units
        self.boundaries_list = boundaries
        self.units = {u.id: u for u in units}
        self.boundaries = {b.id: b for b in boundaries}
        
        self.unit_to_prev_boundary: Dict[uuid.UUID, Any] = {}
        self.unit_to_next_boundary: Dict[uuid.UUID, Any] = {}
        
        for b in boundaries:
            if b.previous_unit_id:
                self.unit_to_next_boundary[b.previous_unit_id] = b
            if b.next_unit_id:
                self.unit_to_prev_boundary[b.next_unit_id] = b

    def previous(self, unit: Any) -> Optional[Any]:
        return self.unit_to_prev_boundary.get(unit.id)

    def next(self, unit: Any) -> Optional[Any]:
        return self.unit_to_next_boundary.get(unit.id)

    def neighbors(self, unit: Any) -> Tuple[Optional[Any], Optional[Any]]:
        return self.previous(unit), self.next(unit)

    def find_boundary(self, boundary_id: uuid.UUID) -> Optional[Any]:
        return self.boundaries.get(boundary_id)

    def find_path(self, start_unit_id: uuid.UUID, end_unit_id: uuid.UUID) -> List[uuid.UUID]:
        path = []
        curr_id = start_unit_id
        visited = set()
        
        while curr_id and curr_id not in visited:
            path.append(curr_id)
            if curr_id == end_unit_id:
                break
            visited.add(curr_id)
            
            next_b = self.unit_to_next_boundary.get(curr_id)
            if next_b:
                curr_id = next_b.next_unit_id
            else:
                curr_id = None
                
        return path

    # Export Visualization support
    def export_mermaid(self) -> str:
        lines = ["graph TD"]
        for u in self.units_list:
            content_snippet = u.content[:20].replace('"', '\\"') + "..."
            lines.append(f"  Unit_{str(u.id)[:8]}[\"Unit ({u.semantic_type}): {content_snippet}\"]")

        for b in self.boundaries_list:
            if b.previous_unit_id and b.next_unit_id:
                label = f"{b.boundary_type} (conf: {b.final_confidence:.2f})"
                lines.append(f"  Unit_{str(b.previous_unit_id)[:8]} -->|\"{label}\"| Unit_{str(b.next_unit_id)[:8]}")
            elif b.previous_unit_id:
                lines.append(f"  Unit_{str(b.previous_unit_id)[:8]} --> DocumentEnd[\"DOCUMENT_END\"]")

        return "\n".join(lines)

    def export_json(self) -> str:
        data = {
            "units": [
                {
                    "id": str(u.id),
                    "semantic_type": u.semantic_type,
                    "content_snippet": u.content[:50]
                }
                for u in self.units_list
            ],
            "boundaries": [b.to_dict() for b in self.boundaries_list]
        }
        return json.dumps(data, indent=2, default=str)

    def export_graphviz(self) -> str:
        lines = ["digraph G {", "  node [shape=box];"]
        for u in self.units_list:
            content_snippet = u.content[:20].replace('"', '\\"')
            lines.append(f"  \"unit_{str(u.id)[:8]}\" [label=\"{u.semantic_type}: {content_snippet}\"];")

        for b in self.boundaries_list:
            if b.previous_unit_id and b.next_unit_id:
                label = f"{b.boundary_type} ({b.final_confidence:.2f})"
                lines.append(f"  \"unit_{str(b.previous_unit_id)[:8]}\" -> \"unit_{str(b.next_unit_id)[:8]}\" [label=\"{label}\"];")
            elif b.previous_unit_id:
                lines.append(f"  \"unit_{str(b.previous_unit_id)[:8]}\" -> \"doc_end\" [label=\"DOCUMENT_END\"];")

        lines.append("}")
        return "\n".join(lines)

    def generate_explanation_report(self) -> BoundaryExplanationReport:
        items = []
        for b in self.boundaries_list:
            matched = getattr(b, "matched_rules", [])
            rejected = getattr(b, "rejected_rules", [])
            quality = getattr(b, "quality_score", 0.0)
            rec = getattr(b, "chunk_recommendation", "preserve")
            
            # Distance breakdown
            dist = getattr(b, "distance_breakdown", {}).get("distance", 0.0)
            
            items.append({
                "id": str(b.id),
                "type": b.boundary_type,
                "matched_rules": matched,
                "rejected_rules": rejected,
                "confidence": b.final_confidence,
                "quality": quality,
                "recommendation": rec,
                "semantic_distance": dist,
                "reason": b.reason
            })
            
        return BoundaryExplanationReport(items)
