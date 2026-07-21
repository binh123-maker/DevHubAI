"""
Retry Policy — Phase 10.6

Deterministic retry strategies for transient stage failures.
"""
from __future__ import annotations
import time
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Type, Tuple

logger = logging.getLogger(__name__)

# Exception types that are always permanent (never retried)
PERMANENT_EXCEPTIONS: Tuple[Type[Exception], ...] = (
    ValueError,
    TypeError,
    KeyError,
    AttributeError,
    NotImplementedError,
)


@dataclass
class RetryPolicy:
    """Deterministic retry policy injected into PipelineRunner."""

    max_retries: int = 2
    retry_delay: float = 0.05          # seconds
    exponential_backoff: bool = True
    backoff_multiplier: float = 2.0
    max_delay: float = 2.0

    # Statistics
    total_retries: int = 0
    successful_retries: int = 0
    failed_retries: int = 0
    retry_log: list = field(default_factory=list)

    def should_retry(self, exc: Exception, attempt: int) -> bool:
        """Return True if the exception is transient and retries remain."""
        if attempt >= self.max_retries:
            return False
        if isinstance(exc, PERMANENT_EXCEPTIONS):
            return False
        return True

    def delay_for(self, attempt: int) -> float:
        """Compute sleep duration for the given attempt index."""
        if not self.exponential_backoff:
            return self.retry_delay
        d = self.retry_delay * (self.backoff_multiplier ** attempt)
        return min(d, self.max_delay)

    def execute_with_retry(self, fn, stage_name: str, *args, **kwargs):
        """Execute *fn* with retry logic; raises on final failure."""
        attempt = 0
        while True:
            try:
                result = fn(*args, **kwargs)
                if attempt > 0:
                    self.successful_retries += 1
                return result
            except Exception as exc:
                if not self.should_retry(exc, attempt):
                    self.failed_retries += 1
                    raise
                delay = self.delay_for(attempt)
                logger.warning(
                    "Stage %s failed (attempt %d/%d). Retrying in %.2fs: %s",
                    stage_name, attempt + 1, self.max_retries, delay, exc
                )
                self.retry_log.append({
                    "stage": stage_name,
                    "attempt": attempt + 1,
                    "error": str(exc),
                    "delay": delay,
                })
                self.total_retries += 1
                time.sleep(delay)
                attempt += 1

    def statistics(self) -> Dict[str, Any]:
        return {
            "total_retries": self.total_retries,
            "successful_retries": self.successful_retries,
            "failed_retries": self.failed_retries,
            "retry_log": self.retry_log,
        }

    @classmethod
    def no_retry(cls) -> "RetryPolicy":
        return cls(max_retries=0)

    @classmethod
    def conservative(cls) -> "RetryPolicy":
        return cls(max_retries=1, retry_delay=0.1)

    @classmethod
    def aggressive(cls) -> "RetryPolicy":
        return cls(max_retries=3, retry_delay=0.05, exponential_backoff=True)
