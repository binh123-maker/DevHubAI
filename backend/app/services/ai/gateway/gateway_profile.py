import time
from typing import Callable, Any, Tuple
from app.services.ai.gateway.gateway_context import GatewayContext

class GatewayProfile:
    @staticmethod
    def profile_execution(ctx: GatewayContext, func: Callable[[], Any]) -> Tuple[Any, float]:
        start = time.time()
        result = func()
        duration_ms = (time.time() - start) * 1000
        ctx.latency_ms = duration_ms
        return result, duration_ms
