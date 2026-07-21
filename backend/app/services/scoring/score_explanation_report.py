import json
from typing import Dict, Any

class ScoreExplanationReport:
    def __init__(self, score: Any):
        self.score = score

    def to_json(self) -> str:
        return json.dumps(self.score.to_dict(), indent=2)

    def to_markdown(self) -> str:
        s = self.score
        lines = [
            f"# Score Explanation Report - {s.score_signature}",
            "",
            f"**Overall Score**: {s.overall_score:.2f} ({s.score_level})",
            f"**Version**: {s.score_version}",
            f"**Recommendation**: {s.recommendation}",
            f"**Confidence**: {s.confidence:.2f}",
            "",
            "## Score Breakdown",
            f"- **Ranking Score**: {s.ranking_score:.2f} (Priority: {s.ranking_priority:.2f})",
            f"- **Quality Score**: {s.quality_score:.2f}",
            f"- **Retrieval Score**: {s.retrieval_score:.2f} (Priority: {s.retrieval_priority:.2f})",
            f"- **Context Priority**: {s.context_priority:.2f}",
            f"- **Recommended Retrieval Mode**: {s.recommended_retrieval_mode}",
            "",
            "## Quality Breakdown Details",
        ]
        for k, v in s.quality_breakdown.items():
            lines.append(f"- **{k.replace('_', ' ').capitalize()}**: {v:.2f}")

        lines.append("\n## Applied Bonuses")
        if s.bonuses:
            for b in s.bonuses:
                lines.append(f"- **{b.get('name')}**: +{b.get('value'):.2f}")
        else:
            lines.append("- None")

        lines.append("\n## Applied Penalties")
        if s.penalties:
            for p in s.penalties:
                lines.append(f"- **{p.get('name')}**: -{p.get('value'):.2f}")
        else:
            lines.append("- None")

        return "\n".join(lines)

    def pretty_print(self) -> str:
        return self.score.pretty_print()
