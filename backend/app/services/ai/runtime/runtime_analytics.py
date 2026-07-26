import time
from typing import Dict, Any, List
from app.services.ai.runtime.runtime_trace import TraceStore

class RuntimeAnalytics:
    """
    Runtime Analytics Engine.
    Analyzes request execution history from TraceStore to compute operational statistics, usage percentages,
    switching frequencies, and error distributions.
    """

    @classmethod
    def get_analytics_report(cls) -> Dict[str, Any]:
        traces = TraceStore.get_all_raw()
        total_traces = len(traces)

        if total_traces == 0:
            return {
                "total_requests": 0,
                "success_rate_pct": 100.0,
                "average_latency_ms": 0.0,
                "average_fallback_count": 0.0,
                "provider_usage_pct": {},
                "capability_usage_pct": {},
                "model_usage_pct": {},
                "most_common_errors": {},
                "provider_switching_frequency": 0,
                "hourly_stats": {},
                "daily_stats": {}
            }

        success_count = 0
        total_latency = 0.0
        total_fallbacks = 0
        provider_counts: Dict[str, int] = {}
        capability_counts: Dict[str, int] = {}
        model_counts: Dict[str, int] = {}
        error_counts: Dict[str, int] = {}
        switching_count = 0
        last_provider = None

        for t in traces:
            if t.status == "SUCCESS":
                success_count += 1
            total_latency += t.latency_ms
            total_fallbacks += t.fallback_count

            p_key = t.selected_provider.lower() if t.selected_provider else "unknown"
            c_key = t.capability.lower() if t.capability else "unknown"
            m_key = t.selected_model.lower() if t.selected_model else "unknown"

            provider_counts[p_key] = provider_counts.get(p_key, 0) + 1
            capability_counts[c_key] = capability_counts.get(c_key, 0) + 1
            model_counts[m_key] = model_counts.get(m_key, 0) + 1

            if t.finish_reason and t.finish_reason not in ("stop", "length"):
                error_counts[t.finish_reason] = error_counts.get(t.finish_reason, 0) + 1

            if last_provider and p_key != last_provider:
                switching_count += 1
            last_provider = p_key

        succ_rate = round((success_count / total_traces) * 100.0, 2)
        avg_lat = round(total_latency / total_traces, 2)
        avg_fallback = round(total_fallbacks / total_traces, 2)

        def to_pct(count_dict: Dict[str, int]) -> Dict[str, float]:
            return {k: round((v / total_traces) * 100.0, 2) for k, v in count_dict.items()}

        return {
            "total_requests": total_traces,
            "success_rate_pct": succ_rate,
            "average_latency_ms": avg_lat,
            "average_fallback_count": avg_fallback,
            "provider_usage_pct": to_pct(provider_counts),
            "capability_usage_pct": to_pct(capability_counts),
            "model_usage_pct": to_pct(model_counts),
            "most_common_errors": error_counts,
            "provider_switching_frequency": switching_count,
            "timestamp": time.time()
        }
