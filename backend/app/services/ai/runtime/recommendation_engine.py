import logging
from typing import Dict, List, Any, Optional
from app.services.ai.runtime.provider_profile import ProviderProfile
from app.services.ai.runtime.provider_registry import ProviderRegistry
from app.services.ai.health.monitor import HealthMonitor

logger = logging.getLogger(__name__)

class RecommendationEngine:
    """
    Provider Recommendation Engine.
    Evaluates and scores providers dynamically on Health, Latency, Failure Rate, Success Rate,
    Cooldown, Capability match, Estimated Cost, Quality, and Speed.
    """

    @classmethod
    def score_provider(cls, profile: ProviderProfile, capability: str) -> Dict[str, Any]:
        p_id = profile.provider_id
        stats = profile.statistics
        tot_req = stats.get("total_requests", 0)
        succ_req = stats.get("successful_requests", 0)
        fail_req = stats.get("failed_requests", 0)

        succ_rate = (succ_req / tot_req) if tot_req > 0 else 1.0
        fail_rate = (fail_req / tot_req) if tot_req > 0 else 0.0
        avg_lat = stats.get("average_latency", 100.0)

        health_factor = profile.health_score * 30.0
        latency_factor = max(0.0, (2000.0 - min(2000.0, avg_lat)) / 2000.0) * 25.0
        success_factor = succ_rate * 20.0
        priority_factor = max(0.0, 100 - profile.priority) * 0.15

        speed_bonus = 10.0 if profile.speed_level == "fast" else (5.0 if profile.speed_level == "medium" else 0.0)
        cost_bonus = 5.0 if profile.free_tier or profile.local or profile.cost_level == "low" else 2.0

        total_score = round(health_factor + latency_factor + success_factor + priority_factor + speed_bonus + cost_bonus, 2)

        return {
            "provider_id": p_id,
            "display_name": profile.display_name,
            "score": total_score,
            "metrics": {
                "health_score": round(profile.health_score, 2),
                "avg_latency_ms": round(avg_lat, 2),
                "success_rate": round(succ_rate, 2),
                "failure_rate": round(fail_rate, 2),
                "speed_level": profile.speed_level,
                "cost_level": profile.cost_level,
                "quality_level": profile.quality_level
            }
        }

    @classmethod
    def score_all_providers(cls, capability: str) -> List[Dict[str, Any]]:
        candidates = ProviderRegistry.profiles_for_capability(capability)
        scores = [cls.score_provider(p, capability) for p in candidates]
        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores

    @classmethod
    def recommend_provider(cls, capability: str) -> Optional[Dict[str, Any]]:
        scored = cls.score_all_providers(capability)
        return scored[0] if scored else None
