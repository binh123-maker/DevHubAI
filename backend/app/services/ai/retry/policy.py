import time
import logging
from typing import Callable, Type, Tuple, Any

logger = logging.getLogger(__name__)

class RetryPolicy:
    def __init__(
        self,
        max_retries: int = 3,
        delay: float = 1.0,
        backoff_factor: float = 2.0,
        retryable_errors: Tuple[Type[Exception], ...] = (Exception,)
    ):
        self.max_retries = max_retries
        self.delay = delay
        self.backoff_factor = backoff_factor
        self.retryable_errors = retryable_errors

    def execute(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        """Execute a function with exponential backoff retries."""
        current_delay = self.delay
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except self.retryable_errors as e:
                last_exception = e
                if attempt == self.max_retries:
                    break
                
                logger.warning(
                    f"[RetryPolicy] Attempt {attempt + 1} failed: {str(e)}. "
                    f"Retrying in {current_delay:.2f} seconds..."
                )
                time.sleep(current_delay)
                current_delay *= self.backoff_factor

        if last_exception:
            raise last_exception
