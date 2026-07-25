from typing import Dict, Any
from app.services.ai.gateway.gateway_context import GatewayContext

class GatewayMetrics:
    _total_requests: int = 0
    _total_fallbacks: int = 0
    _role_counts: Dict[str, int] = {}
    _capability_counts: Dict[str, int] = {}

    @classmethod
    def record_request(cls, ctx: GatewayContext) -> None:
        cls._total_requests += 1
        if len(ctx.fallback_history) > 1:
            cls._total_fallbacks += 1
        role_key = ctx.selected_role.value if hasattr(ctx.selected_role, "value") else str(ctx.selected_role)
        cap_key = ctx.selected_capability.value if hasattr(ctx.selected_capability, "value") else str(ctx.selected_capability)
        cls._role_counts[role_key] = cls._role_counts.get(role_key, 0) + 1
        cls._capability_counts[cap_key] = cls._capability_counts.get(cap_key, 0) + 1

    @classmethod
    def get_summary(cls) -> Dict[str, Any]:
        return {
            "total_requests": cls._total_requests,
            "total_fallbacks": cls._total_fallbacks,
            "role_distribution": dict(cls._role_counts),
            "capability_distribution": dict(cls._capability_counts)
        }

    @classmethod
    def reset(cls) -> None:
        cls._total_requests = 0
        cls._total_fallbacks = 0
        cls._role_counts.clear()
        cls._capability_counts.clear()
