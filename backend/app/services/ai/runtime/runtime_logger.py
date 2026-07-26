import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("app.services.ai.runtime")

class RuntimeLogger:
    """
    Unified Production Runtime Logger.
    Logs execution events with trace ID, provider, capability, latency, and result while strictly scrubbing sensitive keys.
    """

    @classmethod
    def info(cls, trace_id: str, provider: str, capability: str, latency_ms: float, result: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        p_clean = cls._scrub(provider)
        c_clean = cls._scrub(capability)
        logger.info(f"[Trace:{trace_id}] provider='{p_clean}' capability='{c_clean}' latency={latency_ms:.1f}ms result={result}")

    @classmethod
    def warning(cls, trace_id: str, message: str) -> None:
        logger.warning(f"[Trace:{trace_id}] {cls._scrub(message)}")

    @classmethod
    def error(cls, trace_id: str, message: str, exc: Optional[Exception] = None) -> None:
        err_msg = f"[Trace:{trace_id}] {cls._scrub(message)}"
        if exc:
            err_msg += f" Error: {cls._scrub(str(exc))}"
        logger.error(err_msg)

    @classmethod
    def _scrub(cls, text: str) -> str:
        if not isinstance(text, str):
            text = str(text)
        # Scrub potential API keys
        import re
        text = re.sub(r'sk-[A-Za-z0-9_-]{20,}', 'sk-***SCRUBBED***', text)
        text = re.sub(r'gsk_[A-Za-z0-9_-]{20,}', 'gsk_***SCRUBBED***', text)
        return text
