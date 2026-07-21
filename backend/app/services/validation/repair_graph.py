import json
from typing import List, Dict, Any

class RepairGraph:
    def __init__(self, result: Any):
        self.result = result

    def export_mermaid(self) -> str:
        lines = ["graph TD"]
        for idx, issue in enumerate(self.result.repaired_issues):
            lines.append(f"  Chunk_{idx}[\"Chunk {issue.affected_chunk}\"]")
            lines.append(f"  Issue_{idx}[\"Issue {issue.repair_signature}\"]")
            lines.append(f"  Action_{idx}[\"Action {issue.repair_type}\"]")
            
            lines.append(f"  Chunk_{idx} --> Issue_{idx}")
            lines.append(f"  Issue_{idx} --> Action_{idx}")
        return "\n".join(lines)

    def export_graphviz(self) -> str:
        lines = ["digraph G {", "  node [shape=box];"]
        for idx, issue in enumerate(self.result.repaired_issues):
            lines.append(f"  \"chunk_{idx}\" -> \"issue_{idx}\";")
            lines.append(f"  \"issue_{idx}\" -> \"action_{idx}\";")
        lines.append("}")
        return "\n".join(lines)

    def export_json(self) -> str:
        return json.dumps({
            "nodes": [i.to_dict() for i in self.result.repaired_issues]
        }, indent=2)
