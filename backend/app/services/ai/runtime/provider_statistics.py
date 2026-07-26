import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ProviderStatistics:
    """
    Runtime Statistics Engine for AI Providers.
    Tracks executions, tokens, latency, fallbacks, uptime, and updates ProviderProfile statistics dynamically.
    """
    _provider_stats: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def _get_or_create(cls, provider_name: str) -> Dict[str, Any]:
        key = provider_name.lower()
        if key not in cls._provider_stats:
            cls._provider_stats[key] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "fallback_count": 0,
                "total_latency_ms": 0.0,
                "average_latency": 0.0,
                "last_latency": 0.0,
                "average_response_time": 0.0,
                "average_tokens": 0.0,
                "total_prompt_tokens": 0,
                "total_completion_tokens": 0,
                "last_used": None,
                "last_error": None,
                "uptime": 100.0,
                "health_score": 1.0,
                # Legacy aliases for backward compatibility
                "success_count": 0,
                "failure_count": 0,
                "avg_latency_ms": 0.0
            }
        return cls._provider_stats[key]

    @classmethod
    def record_execution(
        cls,
        provider_name: str,
        success: bool,
        latency_ms: float,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        is_fallback: bool = False,
        error_msg: Optional[str] = None
    ) -> None:
        key = provider_name.lower()
        stats = cls._get_or_create(key)
        now = time.time()

        stats["total_requests"] += 1
        stats["last_used"] = now
        stats["last_latency"] = latency_ms

        if is_fallback:
            stats["fallback_count"] += 1

        if success:
            stats["successful_requests"] += 1
            stats["success_count"] += 1
        else:
            stats["failed_requests"] += 1
            stats["failure_count"] += 1
            stats["last_error"] = error_msg or "Execution failure"

        stats["total_latency_ms"] += latency_ms
        tot_req = stats["total_requests"]
        stats["average_latency"] = stats["total_latency_ms"] / tot_req
        stats["avg_latency_ms"] = stats["average_latency"]
        stats["average_response_time"] = stats["average_latency"] / 1000.0

        stats["total_prompt_tokens"] += prompt_tokens
        stats["total_completion_tokens"] += completion_tokens
        tot_tokens = stats["total_prompt_tokens"] + stats["total_completion_tokens"]
        stats["average_tokens"] = tot_tokens / tot_req if tot_req > 0 else 0.0

        # Calculate uptime and health score
        succ = stats["successful_requests"]
        stats["uptime"] = (succ / tot_req * 100.0) if tot_req > 0 else 100.0
        stats["health_score"] = (succ / tot_req) if tot_req > 0 else 1.0

        # Sync to ProviderProfile in ProviderRegistry
        try:
            from app.services.ai.runtime.provider_registry import ProviderRegistry
            profile = ProviderRegistry.get(key)
            if profile:
                profile.statistics = dict(stats)
                profile.health_score = stats["health_score"]
        except Exception:
            pass

    @classmethod
    def get_stats(cls, provider_name: str) -> Dict[str, Any]:
        return dict(cls._get_or_create(provider_name))

    @classmethod
    def get_summary(cls) -> Dict[str, Any]:
        return dict(cls._provider_stats)

    @classmethod
    def reset(cls) -> None:
        cls._provider_stats.clear()
