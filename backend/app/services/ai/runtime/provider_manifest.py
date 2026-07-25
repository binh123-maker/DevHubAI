import json
from typing import Dict, Any, List
from app.services.ai.runtime.provider_registry import ProviderRegistry
from app.services.ai.health.monitor import HealthMonitor

class ProviderManifest:
    @classmethod
    def get_manifest(cls) -> Dict[str, Any]:
        profiles = ProviderRegistry.list_registered_profiles()
        health_snapshot = HealthMonitor.get_health_snapshot()

        manifest_profiles: List[Dict[str, Any]] = []
        for p in profiles:
            h = health_snapshot.get(p.provider_id.lower(), {})
            manifest_profiles.append({
                "provider_id": p.provider_id,
                "display_name": p.display_name,
                "enabled": p.enabled,
                "priority": p.priority,
                "supported_models": p.supported_models,
                "capabilities": [c.value for c in p.capabilities],
                "status": h.get("status", "HEALTHY"),
                "avg_latency_ms": h.get("latency_ms", 0.0),
                "features": {
                    "supports_streaming": p.supports_streaming,
                    "supports_json": p.supports_json,
                    "supports_tools": p.supports_tools,
                    "supports_reasoning": p.supports_reasoning,
                    "supports_multimodal": p.supports_multimodal,
                    "supports_embeddings": p.supports_embeddings
                }
            })

        return {
            "version": "10.7.0",
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
            f"**Total Registered Providers**: {data['total_registered_providers']}",
            "",
            "| Provider | Display Name | Enabled | Priority | Status | Avg Latency | Models |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
        ]
        for p in data["providers"]:
            models_str = ", ".join(p["supported_models"])
            lines.append(f"| `{p['provider_id']}` | {p['display_name']} | {p['enabled']} | {p['priority']} | `{p['status']}` | {p['avg_latency_ms']:.1f}ms | {models_str} |")
        return "\n".join(lines)

    @classmethod
    def generate_html(cls) -> str:
        data = cls.get_manifest()
        rows = []
        for p in data["providers"]:
            rows.append(f"<tr><td>{p['provider_id']}</td><td>{p['display_name']}</td><td>{p['status']}</td><td>{p['avg_latency_ms']:.1f}ms</td></tr>")
        return f"<html><body><h1>Provider Manifest v{data['version']}</h1><table>{''.join(rows)}</table></body></html>"
