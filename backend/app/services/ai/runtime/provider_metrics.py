from typing import Dict, Any, List

class ProviderMetrics:
    """
    Telemetry and Metrics Engine for AI Providers.
    Tracks execution counts, fallbacks, capability distributions, failure reasons, and token averages.
    """
    _total_executions: int = 0
    _total_fallbacks: int = 0
    _total_cooldown_events: int = 0
    _provider_usage_counts: Dict[str, int] = {}
    _capability_usage_counts: Dict[str, int] = {}
    _failure_reasons: Dict[str, int] = {}

    @classmethod
    def record_runtime_execution(
        cls,
        provider_name: str,
        capability: str,
        was_fallback: bool = False,
        error_type: str = None
    ) -> None:
        cls._total_executions += 1
        if was_fallback:
            cls._total_fallbacks += 1

        p_key = provider_name.lower()
        c_key = capability.lower()
        cls._provider_usage_counts[p_key] = cls._provider_usage_counts.get(p_key, 0) + 1
        cls._capability_usage_counts[c_key] = cls._capability_usage_counts.get(c_key, 0) + 1

        if error_type:
            e_key = error_type.lower()
            cls._failure_reasons[e_key] = cls._failure_reasons.get(e_key, 0) + 1

    @classmethod
    def record_cooldown(cls) -> None:
        cls._total_cooldown_events += 1

    @classmethod
    def get_metrics_report(cls) -> Dict[str, Any]:
        usage_percentages = {}
        if cls._total_executions > 0:
            for p, count in cls._provider_usage_counts.items():
                usage_percentages[p] = round((count / cls._total_executions) * 100, 2)

        return {
            "total_executions": cls._total_executions,
            "total_fallbacks": cls._total_fallbacks,
            "total_cooldown_events": cls._total_cooldown_events,
            "provider_counts": dict(cls._provider_usage_counts),
            "provider_usage_percentages": usage_percentages,
            "capability_counts": dict(cls._capability_usage_counts),
            "failure_reasons": dict(cls._failure_reasons)
        }

    @classmethod
    def reset(cls) -> None:
        cls._total_executions = 0
        cls._total_fallbacks = 0
        cls._total_cooldown_events = 0
        cls._provider_usage_counts.clear()
        cls._capability_usage_counts.clear()
        cls._failure_reasons.clear()
