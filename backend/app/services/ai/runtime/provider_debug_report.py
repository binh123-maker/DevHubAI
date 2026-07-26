import json
import time
from typing import Dict, Any
from app.services.ai.runtime.provider_registry import ProviderRegistry
from app.services.ai.runtime.runtime_analytics import RuntimeAnalytics
from app.services.ai.runtime.provider_recommendation_engine import ProviderRecommendationEngine
from app.services.ai.runtime.runtime_timeline import RuntimeTimeline
from app.services.ai.health.monitor import HealthMonitor
from app.services.ai.config.provider_model import ProviderModel

class ProviderDebugReport:
    """
    Provider Diagnostics & Debug Report Exporter.
    Generates structured Markdown, JSON, and HTML reports covering Provider Statistics, Model Statistics,
    Capability Statistics, Timeline, Fallback History, Ranking, Recommendations, Model Resolution, and Analytics.
    """

    @classmethod
    def get_report(cls) -> Dict[str, Any]:
        analytics = RuntimeAnalytics.get_analytics_report()
        recommendations = ProviderRecommendationEngine.recommend_all()
        health_snapshot = HealthMonitor.get_health_snapshot()
        timeline = RuntimeTimeline.get_last_timeline()

        profiles = ProviderRegistry.list_registered_profiles()
        model_resolution = {
            p.provider_id.lower(): ProviderModel.get_resolution_details(p.provider_id.lower())
            for p in profiles
        }

        return {
            "timestamp": time.time(),
            "health_summary": health_snapshot,
            "analytics_summary": analytics,
            "recommendations": recommendations,
            "model_resolution": model_resolution,
            "recent_timeline": timeline
        }

    @classmethod
    def generate_json(cls) -> str:
        return json.dumps(cls.get_report(), indent=2)

    @classmethod
    def generate_markdown(cls) -> str:
        rep = cls.get_report()
        analytics = rep["analytics_summary"]
        lines = [
            "# AI Operations Center — Diagnostics & Debug Report",
            f"**Total Requests Processed**: {analytics.get('total_requests', 0)}",
            f"**Success Rate**: `{analytics.get('success_rate_pct', 100.0)}%`",
            f"**Average Latency**: `{analytics.get('average_latency_ms', 0.0)}ms`",
            f"**Average Fallback Count**: `{analytics.get('average_fallback_count', 0.0)}`",
            "",
            "## Model Resolution & Environment Synchronization",
            "| Provider | Resolved Model | Source | Override Applied |",
            "| :--- | :--- | :--- | :--- |"
        ]
        for p_id, res in rep.get("model_resolution", {}).items():
            lines.append(f"| `{p_id}` | `{res.get('resolved_model')}` | `{res.get('model_source')}` | {res.get('override_applied')} |")

        lines.extend([
            "",
            "## Telemetry-Based Provider Recommendations",
            "| Capability | Recommended Provider | Score |",
            "| :--- | :--- | :--- |"
        ])
        for cap, rec in rep["recommendations"].items():
            lines.append(f"| `{cap}` | `{rec.get('recommended_provider', 'N/A')}` | {rec.get('score', 0.0)} |")

        lines.extend([
            "",
            "## Timeline Details",
            RuntimeTimeline.generate_markdown()
        ])
        return "\n".join(lines)

    @classmethod
    def generate_html(cls) -> str:
        rep = cls.get_report()
        return f"<html><body><h1>AI Diagnostics Report</h1><pre>{json.dumps(rep, indent=2)}</pre></body></html>"
