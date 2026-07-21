import json
from typing import List, Dict, Any

class ValidationGraph:
    def __init__(self, result: Any):
        self.result = result

    def export_mermaid(self) -> str:
        lines = ["graph TD"]
        for idx, issue in enumerate(self.result.issues):
            lines.append(f"  Chunk_{idx}[\"Chunk {issue.affected_chunk}\"]")
            lines.append(f"  Rule_{idx}[\"Rule {issue.rule_name}\"]")
            lines.append(f"  Issue_{idx}[\"Issue {issue.issue_signature}\"]")
            lines.append(f"  Rec_{idx}[\"Recommendation {issue.recommendation}\"]")
            
            lines.append(f"  Chunk_{idx} --> Rule_{idx}")
            lines.append(f"  Rule_{idx} --> Issue_{idx}")
            lines.append(f"  Issue_{idx} --> Rec_{idx}")
        return "\n".join(lines)

    def export_graphviz(self) -> str:
        lines = ["digraph G {", "  node [shape=box];"]
        for idx, issue in enumerate(self.result.issues):
            lines.append(f"  \"chunk_{idx}\" -> \"rule_{idx}\";")
            lines.append(f"  \"rule_{idx}\" -> \"issue_{idx}\";")
            lines.append(f"  \"issue_{idx}\" -> \"rec_{idx}\";")
        lines.append("}")
        return "\n".join(lines)

    def export_json(self) -> str:
        return json.dumps({
            "nodes": [i.to_dict() for i in self.result.issues]
        }, indent=2)
        
    def rule_graph(self) -> Dict[str, Any]:
        return {"type": "RuleGraph"}
        
    def issue_graph(self) -> Dict[str, Any]:
        return {"type": "IssueGraph"}

    def chunk_dependency_graph(self) -> Dict[str, Any]:
        return {"type": "ChunkDependencyGraph"}

    def validation_flow_graph(self) -> Dict[str, Any]:
        return {"type": "ValidationFlowGraph"}

    def pipeline_health_graph(self) -> Dict[str, Any]:
        return {"type": "PipelineHealthGraph"}
