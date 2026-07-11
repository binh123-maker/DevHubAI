import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = "CLOSED"  # CLOSED, OPEN, HALF-OPEN
        self.failure_count = 0

    def call(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        """
        Execute a function wrapped by the circuit breaker.
        Saves failures and transitions states when thresholds are crossed.
        """
        if self.state == "OPEN":
            raise Exception("Circuit breaker is OPEN. Calls are temporarily blocked.")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "HALF-OPEN":
                logger.info("[CircuitBreaker] Closed successfully.")
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                logger.error(f"[CircuitBreaker] Tripped to OPEN state due to {self.failure_count} failures.")
                self.state = "OPEN"
            raise e
