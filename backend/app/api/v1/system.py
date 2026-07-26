from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from app.services.ai.runtime import (
    ProviderRegistry,
    ProviderManifest,
    ProviderMetrics,
    TraceStore,
    RuntimeDashboard,
    RuntimeAnalytics,
    ProviderRecommendationEngine,
    RuntimeTimeline
)
from app.services.ai.policy import PolicyEngine
from app.services.ai.health.monitor import HealthMonitor

router = APIRouter()

@router.get("/providers")
def get_system_providers():
    return ProviderManifest.get_manifest()

@router.get("/providers/ranking")
def get_provider_rankings():
    return {
        "active_policy": PolicyEngine.get_policy(),
        "rankings": ProviderRecommendationEngine.recommend_for_capability("chat")
    }

@router.get("/providers/recommendations")
def get_provider_recommendations():
    return ProviderRecommendationEngine.recommend_all()

@router.get("/runtime")
def get_system_runtime():
    return RuntimeDashboard.get_snapshot()

@router.get("/runtime/config")
def get_system_runtime_config():
    from app.services.ai.config.provider_env_loader import ProviderEnvLoader
    profiles = ProviderRegistry.list_registered_profiles()
    return [
        {
            "provider": p.provider_id,
            "model": p.default_model,
            "base_url": p.base_url or ProviderEnvLoader.get_base_url(p.provider_id) or "N/A",
            "enabled": p.enabled,
            "source": "ProviderProfile"
        }
        for p in profiles
    ]

@router.get("/runtime/traces")
def get_runtime_traces(limit: int = 50):
    return {
        "total_traces": len(TraceStore.get_all_raw()),
        "recent_traces": TraceStore.get_recent_traces(limit=limit)
    }

@router.get("/runtime/metrics")
def get_runtime_metrics():
    return ProviderMetrics.get_metrics_report()

@router.get("/analytics")
def get_runtime_analytics():
    return RuntimeAnalytics.get_analytics_report()

@router.get("/analytics/models")
def get_analytics_models():
    report = RuntimeAnalytics.get_analytics_report()
    return {"model_usage_pct": report.get("model_usage_pct", {})}

@router.get("/analytics/capabilities")
def get_analytics_capabilities():
    report = RuntimeAnalytics.get_analytics_report()
    return {"capability_usage_pct": report.get("capability_usage_pct", {})}

@router.get("/analytics/errors")
def get_analytics_errors():
    report = RuntimeAnalytics.get_analytics_report()
    return {"most_common_errors": report.get("most_common_errors", {})}

@router.get("/analytics/fallbacks")
def get_analytics_fallbacks():
    report = RuntimeAnalytics.get_analytics_report()
    return {
        "total_requests": report.get("total_requests", 0),
        "average_fallback_count": report.get("average_fallback_count", 0.0),
        "switching_frequency": report.get("provider_switching_frequency", 0)
    }

@router.get("/timeline/{trace_id}")
def get_timeline_by_trace(trace_id: str):
    trace = TraceStore.get_trace(trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail=f"Trace ID '{trace_id}' not found.")
    return {
        "trace": trace,
        "timeline_json": RuntimeTimeline.get_last_timeline(),
        "mermaid_sequence": RuntimeTimeline.generate_mermaid_sequence(),
        "mermaid_flowchart": RuntimeTimeline.generate_mermaid_flowchart()
    }
