import json
from typing import Dict, Any, List
from app.services.ai.runtime.provider_registry import ProviderRegistry
from app.services.ai.runtime.provider_selector import ProviderSelector
from app.services.ai.runtime.provider_alias import ProviderAlias
from app.services.ai.runtime.recommendation_engine import RecommendationEngine
from app.services.ai.runtime.runtime_timeline import RuntimeTimeline
from app.services.ai.policy.policy_engine import PolicyEngine
from app.services.ai.health.monitor import HealthMonitor

class ProviderManifest:
    """
    AI Runtime Manifest Exporter.
    Generates structured Markdown, JSON, and HTML manifest documents including Providers,
    Policies, Capabilities, Models, Health, Statistics, Recommendations, Configuration,
    and Timeline Summaries.
    """

    @classmethod
    def get_manifest(cls) -> Dict[str, Any]:
        profiles = ProviderRegistry.list_registered_profiles()
        health_snapshot = HealthMonitor.get_health_snapshot()
        current_policy = PolicyEngine.get_policy()
        current_group_policy = ProviderSelector.get_group_policy()
        aliases = ProviderAlias.list_aliases()
        recommendations = RecommendationEngine.score_all_providers("chat")

        manifest_profiles: List[Dict[str, Any]] = []
        for p in profiles:
            h = health_snapshot.get(p.provider_id.lower(), {})
            status = p.health_status or h.get("status", "ONLINE")
            avg_lat = p.statistics.get("average_latency", h.get("latency_ms", 0.0))
            score = p.calculate_score(current_policy)

            manifest_profiles.append({
                "provider_id": p.provider_id,
                "display_name": p.display_name,
                "description": p.description,
                "enabled": p.enabled,
                "priority": p.priority,
                "group": p.group,
                "score": round(score, 2),
                "status": status,
                "health_score": round(p.health_score, 2),
                "default_model": p.default_model,
                "supported_models": p.supported_models,
                "capabilities": [c.value if hasattr(c, "value") else str(c) for c in p.capabilities],
                "avg_latency_ms": round(avg_lat, 2),
                "total_requests": p.statistics.get("total_requests", 0),
                "successful_requests": p.statistics.get("successful_requests", 0),
                "failed_requests": p.statistics.get("failed_requests", 0),
                "fallback_count": p.statistics.get("fallback_count", 0),
                "total_prompt_tokens": p.statistics.get("total_prompt_tokens", 0),
                "total_completion_tokens": p.statistics.get("total_completion_tokens", 0),
                "limits": {
                    "max_context_tokens": p.max_context_tokens,
                    "max_output_tokens": p.max_output_tokens,
                    "timeout": p.timeout,
                    "cooldown": p.cooldown,
                    "retry_limit": p.retry_limit
                },
                "levels": {
                    "cost_level": p.cost_level,
                    "speed_level": p.speed_level,
                    "quality_level": p.quality_level,
                    "free_tier": p.free_tier,
                    "online": p.online,
                    "local": p.local
                },
                "features": {
                    "supports_chat": p.supports_chat,
                    "supports_streaming": p.supports_streaming,
                    "supports_json": p.supports_json,
                    "supports_tools": p.supports_tools,
                    "supports_reasoning": p.supports_reasoning,
                    "supports_vision": p.supports_vision,
                    "supports_multimodal": p.supports_multimodal,
                    "supports_embeddings": p.supports_embeddings,
                    "supports_function_calling": p.supports_function_calling
                },
                "metadata": {
                    "website_url": p.website_url,
                    "doc_url": p.doc_url,
                    "api_version": p.api_version,
                    "provider_version": p.provider_version,
                    "plugin_version": p.plugin_version,
                    "maintainer": p.maintainer
                }
            })

        return {
            "version": "10.7.0",
            "active_policy": current_policy,
            "active_group_policy": current_group_policy,
            "aliases": aliases,
            "recommendations": recommendations,
            "timeline_summary": RuntimeTimeline.get_last_timeline(),
            "total_registered_providers": len(profiles),
            "providers": manifest_profiles
        }

    @classmethod
    def generate_json(cls) -> str:
        return json.dumps(cls.get_manifest(), indent=2)

    @classmethod
    def generate_markdown(cls) -> str:
        data = cls.get_manifest()
        lines = [
            f"# Provider Manifest (v{data['version']})",
            f"**Active Runtime Policy**: `{data['active_policy']}` | **Active Group Policy**: `{data['active_group_policy']}`",
            f"**Total Registered Providers**: {data['total_registered_providers']}",
            "",
            "## Registered Aliases",
            "| Alias | Resolved Target |",
            "| :--- | :--- |"
        ]
        for alias, target in data["aliases"].items():
            lines.append(f"| `{alias}` | `{target}` |")

        lines.extend([
            "",
            "## Provider Registry & Performance Dashboard",
            "| Provider | Display Name | Group | Enabled | Priority | Score | Status | Avg Latency | Models |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
        ])
        for p in data["providers"]:
            models_str = ", ".join(p["supported_models"])
            lines.append(f"| `{p['provider_id']}` | {p['display_name']} | `{p['group']}` | {p['enabled']} | {p['priority']} | {p['score']} | `{p['status']}` | {p['avg_latency_ms']:.1f}ms | {models_str} |")

        return "\n".join(lines)

    @classmethod
    def generate_html(cls) -> str:
        data = cls.get_manifest()
        rows = []
        for p in data["providers"]:
            rows.append(f"<tr><td>{p['provider_id']}</td><td>{p['display_name']}</td><td>{p['group']}</td><td>{p['status']}</td><td>{p['score']}</td><td>{p['avg_latency_ms']:.1f}ms</td></tr>")
        return f"<html><body><h1>Provider Manifest v{data['version']}</h1><p>Policy: {data['active_policy']}</p><table><tr><th>Provider</th><th>Name</th><th>Group</th><th>Status</th><th>Score</th><th>Latency</th></tr>{''.join(rows)}</table></body></html>"
