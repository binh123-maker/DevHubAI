import time
from typing import Dict, Any, List
from app.services.ai.runtime.provider_registry import ProviderRegistry
from app.services.ai.runtime.provider_selector import ProviderSelector
from app.services.ai.policy.policy_engine import PolicyEngine
from app.services.ai.health.monitor import HealthMonitor

class RuntimeDashboard:
    """
    Runtime Dashboard Snapshot Engine.
    Generates structured backend JSON snapshots for monitoring and future admin dashboards.
    """

    @classmethod
    def get_snapshot(cls) -> Dict[str, Any]:
        profiles = ProviderRegistry.list_registered_profiles()
        health_snapshot = HealthMonitor.get_health_snapshot()
        current_policy = PolicyEngine.get_policy()

        dashboard_providers: List[Dict[str, Any]] = []
        for p in profiles:
            h = health_snapshot.get(p.provider_id.lower(), {})
            tot_req = p.statistics.get("total_requests", 0)
            succ_req = p.statistics.get("successful_requests", 0)
            fail_req = p.statistics.get("failed_requests", 0)
            succ_rate = (succ_req / tot_req * 100.0) if tot_req > 0 else 100.0
            avg_lat = p.statistics.get("average_latency", h.get("latency_ms", 0.0))
            avg_tok = p.statistics.get("average_tokens", 0.0)

            dashboard_providers.append({
                "provider_id": p.provider_id,
                "display_name": p.display_name,
                "enabled": p.enabled,
                "health": p.health_score,
                "health_status": p.health_status or h.get("status", "ONLINE"),
                "status": p.health_status or h.get("status", "ONLINE"),
                "average_latency_ms": round(avg_lat, 2),
                "average_tokens": round(avg_tok, 2),
                "requests": tot_req,
                "failures": fail_req,
                "success_rate_pct": round(succ_rate, 2),
                "cooldown": p.cooldown,
                "current_model": p.default_model or "gpt-4o",
                "priority": p.priority,
                "capabilities": [c.value if hasattr(c, "value") else str(c) for c in p.capabilities],
                "levels": {
                    "cost_level": p.cost_level,
                    "quality_level": p.quality_level,
                    "speed_level": p.speed_level
                },
                "policy": current_policy
            })

        return {
            "timestamp": time.time(),
            "active_policy": current_policy,
            "total_providers": len(profiles),
            "healthy_providers": len(ProviderRegistry.healthy_profiles()),
            "providers": dashboard_providers
        }
