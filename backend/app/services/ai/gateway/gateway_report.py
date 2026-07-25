from typing import Dict, Any
from app.services.ai.gateway.gateway_context import GatewayContext

class GatewayReport:
    @staticmethod
    def generate_execution_report(ctx: GatewayContext) -> Dict[str, Any]:
        return {
            "trace_id": ctx.trace_id,
            "conversation_id": ctx.conversation_id,
            "task_type": ctx.task_type.value if hasattr(ctx.task_type, "value") else str(ctx.task_type),
            "role": ctx.selected_role.value if hasattr(ctx.selected_role, "value") else str(ctx.selected_role),
            "capability": ctx.selected_capability.value if hasattr(ctx.selected_capability, "value") else str(ctx.selected_capability),
            "provider": ctx.selected_provider,
            "model": ctx.selected_model,
            "latency_ms": ctx.latency_ms,
            "fallback_attempts": len(ctx.fallback_history) - 1 if ctx.fallback_history else 0,
            "execution_trace": ctx.execution_trace,
            "fallback_history": ctx.fallback_history
        }
