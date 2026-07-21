import json
from typing import Any, Dict

class ValidationExplanationReport:
    def __init__(self, result: Any):
        self.result = result

    def to_json(self) -> str:
        return json.dumps(self.result.to_dict(), indent=2)

    def to_markdown(self) -> str:
        r = self.result
        lines = [
            f"# Semantic Validation Explanation Report",
            "",
            f"**Validation Status**: {r.overall_status}",
            f"**Pipeline Health Score**: {r.pipeline_health_score:.2f}",
            f"**Retrieval Readiness Score**: {r.retrieval_readiness_score:.2f}",
            f"**Overall Validation Score**: {r.overall_validation_score:.2f}",
            "",
            "## Summary statistics",
            f"- **Passed Rules**: {r.passed_rules} / {r.total_rules}",
            f"- **Critical Issues**: {r.critical_count}",
            f"- **Warning Issues**: {r.warning_count}",
            f"- **Info Issues**: {r.info_count}",
            "",
            "## Detected Validation Issues",
            "| Signature | Severity | Category | Subcategory | Description | Repair Hint |",
            "|---|---|---|---|---|---|",
        ]
        
        for issue in r.issues:
            lines.append(
                f"| {issue.issue_signature} | {issue.severity} | {issue.category} | "
                f"{issue.subcategory} | {issue.description} | {issue.repair_hint} |"
            )
            
        return "\n".join(lines)

    def to_html(self) -> str:
        r = self.result
        return f"<html><body><h1>Validation Score: {r.overall_validation_score:.2f}</h1></body></html>"

    def pretty_print(self) -> str:
        r = self.result
        return f"=== Semantic Validation Results ===\nStatus: {r.overall_status}\nScore: {r.overall_validation_score:.2f}\nIssues: {len(r.issues)}"
