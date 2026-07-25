import logging
from typing import List, Dict, Callable, Any, Optional, Tuple
from app.services.ai.health.monitor import HealthMonitor
from app.services.ai.exceptions import (
    AIError,
    AuthenticationError,
    ProviderUnavailableError,
    RateLimitError,
    TimeoutError,
    GenerationError,
    ConfigurationError
)

logger = logging.getLogger(__name__)

class FallbackManager:
    @classmethod
    def execute_with_fallback(
        cls,
        candidate_chain: List[Dict[str, str]],
        callable_func: Callable[[str, str], Any]
    ) -> Tuple[Any, List[dict]]:
        """
        Executes callable_func(provider, model) through the candidate chain.
        Applies deterministic fallback rules on failure, updating HealthMonitor.
        Returns (result, fallback_history).
        """
        fallback_history: List[dict] = []
        last_exception: Optional[Exception] = None

        for candidate in candidate_chain:
            provider = candidate["provider"]
            model = candidate["model"]

            # Check health before invocation
            if not HealthMonitor.is_provider_healthy(provider):
                logger.info(f"[FallbackManager] Provider '{provider}' skipped due to unhealthy status/cooldown.")
                fallback_history.append({
                    "provider": provider,
                    "model": model,
                    "status": "SKIPPED_UNHEALTHY",
                    "error": "Provider in cooldown/offline/unauthorized state"
                })
                continue

            try:
                logger.info(f"[FallbackManager] Attempting execution with provider='{provider}', model='{model}'")
                result = callable_func(provider, model)
                # Success
                fallback_history.append({
                    "provider": provider,
                    "model": model,
                    "status": "SUCCESS"
                })
                return result, fallback_history
            except Exception as exc:
                last_exception = exc
                error_type = type(exc).__name__
                error_msg = str(exc)
                logger.warning(f"[FallbackManager] Provider '{provider}' failed with {error_type}: {error_msg}")

                # Determine HTTP status code mapping if available
                status_code = None
                if isinstance(exc, AuthenticationError):
                    status_code = 401
                elif isinstance(exc, RateLimitError):
                    status_code = 429
                elif isinstance(exc, TimeoutError):
                    status_code = 408
                elif isinstance(exc, ProviderUnavailableError):
                    status_code = 503

                # Record failure in HealthMonitor
                HealthMonitor.record_failure(
                    provider=provider,
                    error_type=error_type,
                    status_code=status_code
                )

                fallback_history.append({
                    "provider": provider,
                    "model": model,
                    "status": "FAILED",
                    "error_type": error_type,
                    "error": error_msg
                })

        # If all candidates failed
        error_summary = f"All provider candidates in fallback chain failed. Last error: {str(last_exception)}"
        logger.error(f"[FallbackManager] {error_summary}")
        if last_exception:
            raise last_exception
        raise AIError(error_summary)
