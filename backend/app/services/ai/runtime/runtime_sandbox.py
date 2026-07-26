import logging
from typing import Dict, Any, Optional
from app.services.ai.health.monitor import HealthMonitor

logger = logging.getLogger(__name__)

class RuntimeSandbox:
    """
    Runtime Simulation Sandbox for Error Simulation & Fallback Testing.
    Allows developers to simulate 401, 403, 404, 429, 500, timeout, network failure, and provider offline
    states safely without altering actual provider credentials or external connections.
    """

    @classmethod
    def simulate_failure(
        cls,
        provider: str,
        error_code: int = 429,
        error_type: str = "RateLimitError",
        cooldown_seconds: float = 60.0
    ) -> Dict[str, Any]:
        p_id = provider.lower()
        logger.info(f"[RuntimeSandbox] Simulating failure error_code={error_code} error_type='{error_type}' for provider '{p_id}'")

        # Record simulated failure in HealthMonitor
        HealthMonitor.record_failure(
            provider=p_id,
            error_type=error_type,
            status_code=error_code,
            cooldown_seconds=cooldown_seconds
        )

        from app.services.ai.runtime.provider_registry import ProviderRegistry
        profile = ProviderRegistry.get(p_id)

        return {
            "simulation_success": True,
            "provider_id": p_id,
            "simulated_error_code": error_code,
            "simulated_error_type": error_type,
            "resulting_health_status": profile.health_status if profile else "COOLDOWN",
            "is_healthy": HealthMonitor.is_provider_healthy(p_id)
        }

    @classmethod
    def clear_simulation(cls, provider: str) -> None:
        HealthMonitor.resume(provider)
        logger.info(f"[RuntimeSandbox] Cleared simulated failure for provider '{provider}'")
