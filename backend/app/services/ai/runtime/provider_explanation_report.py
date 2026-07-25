import json
from typing import Dict, Any, List

class ProviderExplanationReport:
    @staticmethod
    def generate_markdown(
        capability: str,
        selected_provider: str,
        selected_model: str,
        candidate_chain: List[dict],
        fallback_history: List[dict],
        latency_ms: float
    ) -> str:
        lines = [
            f"# Provider Execution Report",
            f"- **Capability**: `{capability}`",
            f"- **Selected Provider**: `{selected_provider}`",
            f"- **Model Used**: `{selected_model}`",
            f"- **Latency**: `{latency_ms:.1f}ms`",
            f"",
            f"## Candidate Chain Resolution",
        ]
        for idx, candidate in enumerate(candidate_chain, 1):
            lines.append(f"{idx}. Provider: `{candidate['provider']}` | Model: `{candidate['model']}`")

        lines.append("")
        lines.append("## Execution & Fallback History")
        for step in fallback_history:
            status = step.get("status", "UNKNOWN")
            p = step.get("provider", "unknown")
            m = step.get("model", "unknown")
            if status == "SUCCESS":
                lines.append(f"- ✅ `{p}` ({m}): Executed successfully.")
            elif status == "FAILED":
                err = step.get("error", "Unknown error")
                lines.append(f"- ❌ `{p}` ({m}): Failed - {err}")
            elif status == "SKIPPED_UNHEALTHY":
                lines.append(f"- ⚠️ `{p}` ({m}): Skipped due to unhealthy status/cooldown.")

        return "\n".join(lines)

    @staticmethod
    def generate_json(
        capability: str,
        selected_provider: str,
        selected_model: str,
        candidate_chain: List[dict],
        fallback_history: List[dict],
        latency_ms: float
    ) -> str:
        data = {
            "capability": capability,
            "selected_provider": selected_provider,
            "selected_model": selected_model,
            "latency_ms": latency_ms,
            "candidate_chain": candidate_chain,
            "fallback_history": fallback_history
        }
        return json.dumps(data, indent=2)
