import logging
from typing import Dict, Any, List, Optional
from app.services.ai.runtime.provider_registry import ProviderRegistry
from app.services.ai.runtime.runtime_analytics import RuntimeAnalytics

logger = logging.getLogger(__name__)

class ProviderRecommendationEngine:
    """
    Provider Recommendation Engine (Telemetry-Based).
    Analyzes live performance telemetry to recommend optimal providers per capability.
    """

    @classmethod
    def recommend_for_capability(cls, capability: str) -> Dict[str, Any]:
        candidates = ProviderRegistry.profiles_for_capability(capability)
        if not candidates:
            return {"capability": capability, "recommended_provider": "openai", "reason": "Default fallback"}

        # Score candidates based on profile priority, health score, latency, and success rate
        scored: List[Dict[str, Any]] = []
        for p in candidates:
            stats = p.statistics
            avg_lat = stats.get("average_latency", 100.0)
            succ_rate = (stats.get("successful_requests", 0) / stats["total_requests"]) if stats.get("total_requests", 0) > 0 else 1.0
            
            score = (p.health_score * 40.0) + (succ_rate * 30.0) + max(0.0, (2000.0 - min(2000.0, avg_lat)) / 2000.0) * 20.0 + max(0, 100 - p.priority) * 0.1
            scored.append({
                "provider_id": p.provider_id,
                "display_name": p.display_name,
                "score": round(score, 2),
                "avg_latency_ms": round(avg_lat, 2),
                "health_status": p.health_status
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        top = scored[0]

        return {
            "capability": capability,
            "recommended_provider": top["provider_id"],
            "display_name": top["display_name"],
            "score": top["score"],
            "candidates_evaluated": len(scored),
            "rankings": scored
        }

    @classmethod
    def recommend_all(cls) -> Dict[str, Any]:
        capabilities = ["chat", "reasoning", "rag", "coding", "summarization", "embedding"]
        return {cap: cls.recommend_for_capability(cap) for cap in capabilities}
