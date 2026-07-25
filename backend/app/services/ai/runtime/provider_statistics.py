from typing import Dict, Any

class ProviderStatistics:
    _provider_stats: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def record_execution(
        cls,
        provider_name: str,
        success: bool,
        latency_ms: float,
        prompt_tokens: int = 0,
        completion_tokens: int = 0
    ) -> None:
        key = provider_name.lower()
        if key not in cls._provider_stats:
            cls._provider_stats[key] = {
                "total_requests": 0,
                "success_count": 0,
                "failure_count": 0,
                "total_latency_ms": 0.0,
                "avg_latency_ms": 0.0,
                "total_prompt_tokens": 0,
                "total_completion_tokens": 0
            }
        stats = cls._provider_stats[key]
        stats["total_requests"] += 1
        if success:
            stats["success_count"] += 1
        else:
            stats["failure_count"] += 1

        stats["total_latency_ms"] += latency_ms
        stats["avg_latency_ms"] = stats["total_latency_ms"] / stats["total_requests"]
        stats["total_prompt_tokens"] += prompt_tokens
        stats["total_completion_tokens"] += completion_tokens

    @classmethod
    def get_summary(cls) -> Dict[str, Any]:
        return dict(cls._provider_stats)

    @classmethod
    def reset(cls) -> None:
        cls._provider_stats.clear()
