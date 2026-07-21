import json
from typing import Any, Dict

class RepairExplanationReport:
    def __init__(self, result: Any):
        self.result = result

    def to_json(self) -> str:
        return json.dumps(self.result.to_dict(), indent=2)

    def to_markdown(self) -> str:
        r = self.result
        lines = [
            f"# Automatic Semantic Repair Explanation Report",
            "",
            f"**Repair Summary**: {r.repair_summary}",
            f"**Repair Score**: {r.repair_score:.2f}",
            f"**Repair Quality Score**: {r.repair_quality:.2f}",
            "",
            "## Repaired Issues",
            "| Signature | Severity | Type | Before State | After State | Confidence |",
            "|---|---|---|---|---|---|",
        ]
        
        for issue in r.repaired_issues:
            lines.append(
                f"| {issue.repair_signature} | {issue.severity} | {issue.repair_type} | "
                f"{issue.before_state} | {issue.after_state} | {issue.confidence:.2f} |"
            )
            
        return "\n".join(lines)

    def to_html(self) -> str:
        r = self.result
        return f"<html><body><h1>Repair Score: {r.repair_score:.2f}</h1></body></html>"

    def pretty_print(self) -> str:
        r = self.result
        return f"=== Repair Results ===\nScore: {r.repair_score:.2f}\nRepaired Issues: {len(r.repaired_issues)}"
