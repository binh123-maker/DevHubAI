import logging
from typing import Optional

logger = logging.getLogger("app.services.ai.metrics")

class MetricsCollector:
    @staticmethod
    def record(
        provider: str,
        model: str,
        latency_ms: float,
        prompt_tokens: Optional[int] = 0,
        completion_tokens: Optional[int] = 0,
        retry_count: int = 0,
        error_type: Optional[str] = None
    ) -> None:
        """Centralized logging for AI metrics."""
        log_msg = (
            f"[AI METRICS] Provider: {provider} | Model: {model} | Latency: {latency_ms:.2f}ms | "
            f"Prompt Tokens: {prompt_tokens or 0} | Completion Tokens: {completion_tokens or 0} | "
            f"Retries: {retry_count} | Error: {error_type or 'None'}"
        )
        if error_type:
            logger.error(log_msg)
        else:
            logger.info(log_msg)
