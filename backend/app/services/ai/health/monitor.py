import time
import logging
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class ProviderHealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    ONLINE = "ONLINE"
    COOLDOWN = "COOLDOWN"
    OFFLINE = "OFFLINE"
    UNAUTHORIZED = "UNAUTHORIZED"
    DISABLED = "DISABLED"
    PAUSED = "PAUSED"
    RATE_LIMIT = "RATE_LIMIT"
    TIMEOUT = "TIMEOUT"

class ProviderMetrics(BaseModel):
    provider_name: str
    status: ProviderHealthStatus = ProviderHealthStatus.HEALTHY
    latency_ms: float = 0.0
    total_requests: int = 0
    success_count: int = 0
    failure_count: int = 0
    consecutive_failures: int = 0
    count_401: int = 0
    count_404: int = 0
    count_429: int = 0
    count_timeout: int = 0
    last_success_timestamp: Optional[float] = None
    cooldown_until: Optional[float] = None

class HealthMonitor:
    """
    Health Monitor Service for AI Providers.
    Tracks live health status, cooldowns, auto-pausing/resuming, and updates ProviderProfile.health_status.
    """
    _metrics_store: Dict[str, ProviderMetrics] = {}

    @classmethod
    def _get_or_create(cls, provider: str) -> ProviderMetrics:
        key = provider.lower()
        if key not in cls._metrics_store:
            cls._metrics_store[key] = ProviderMetrics(provider_name=key)
        return cls._metrics_store[key]

    @classmethod
    def _sync_profile_health(cls, provider: str, status: ProviderHealthStatus) -> None:
        try:
            from app.services.ai.runtime.provider_registry import ProviderRegistry
            profile = ProviderRegistry.get(provider)
            if profile:
                status_str = status.value if hasattr(status, "value") else str(status)
                profile.health_status = status_str
                profile.online = status_str in ("HEALTHY", "ONLINE")
        except Exception:
            pass

    @classmethod
    def is_provider_healthy(cls, provider: str) -> bool:
        metrics = cls._get_or_create(provider)
        now = time.time()

        if metrics.status in (ProviderHealthStatus.COOLDOWN, ProviderHealthStatus.PAUSED, ProviderHealthStatus.OFFLINE, ProviderHealthStatus.UNAUTHORIZED, ProviderHealthStatus.DISABLED, ProviderHealthStatus.RATE_LIMIT, ProviderHealthStatus.TIMEOUT):
            if metrics.cooldown_until and now >= metrics.cooldown_until:
                metrics.status = ProviderHealthStatus.HEALTHY
                metrics.cooldown_until = None
                cls._sync_profile_health(provider, ProviderHealthStatus.HEALTHY)
                logger.info(f"[HealthMonitor] Provider '{provider}' cooldown/pause expired. Transitioned to HEALTHY.")
                return True
            return False

        return True

    @classmethod
    def pause(cls, provider: str, duration_seconds: float = 60.0) -> None:
        metrics = cls._get_or_create(provider)
        metrics.status = ProviderHealthStatus.PAUSED
        metrics.cooldown_until = time.time() + duration_seconds
        cls._sync_profile_health(provider, ProviderHealthStatus.PAUSED)
        logger.warning(f"[HealthMonitor] Paused provider '{provider}' for {duration_seconds}s.")

    @classmethod
    def resume(cls, provider: str) -> None:
        metrics = cls._get_or_create(provider)
        metrics.status = ProviderHealthStatus.HEALTHY
        metrics.cooldown_until = None
        metrics.consecutive_failures = 0
        cls._sync_profile_health(provider, ProviderHealthStatus.HEALTHY)
        logger.info(f"[HealthMonitor] Resumed provider '{provider}'. Status set to HEALTHY.")

    @classmethod
    def record_success(cls, provider: str, latency_ms: float) -> None:
        metrics = cls._get_or_create(provider)
        metrics.total_requests += 1
        metrics.success_count += 1
        metrics.consecutive_failures = 0
        metrics.status = ProviderHealthStatus.HEALTHY
        metrics.last_success_timestamp = time.time()
        cls._sync_profile_health(provider, ProviderHealthStatus.HEALTHY)

        if metrics.latency_ms == 0.0:
            metrics.latency_ms = latency_ms
        else:
            metrics.latency_ms = (metrics.latency_ms * 0.7) + (latency_ms * 0.3)

    @classmethod
    def record_failure(
        cls,
        provider: str,
        error_type: str,
        status_code: Optional[int] = None,
        cooldown_seconds: float = 180.0
    ) -> None:
        metrics = cls._get_or_create(provider)
        metrics.total_requests += 1
        metrics.failure_count += 1
        metrics.consecutive_failures += 1
        now = time.time()
        err_lower = error_type.lower()

        if status_code in (401, 403) or any(k in err_lower for k in ["auth", "unauthorized", "forbidden", "api key"]):
            metrics.count_401 += 1
            metrics.status = ProviderHealthStatus.UNAUTHORIZED
            metrics.cooldown_until = now + 3600.0
            cls._sync_profile_health(provider, ProviderHealthStatus.UNAUTHORIZED)
            logger.warning(f"[HealthMonitor] Provider '{provider}' marked UNAUTHORIZED (401/403). Auto-paused.")

        elif status_code == 404 or "notfound" in err_lower:
            metrics.count_404 += 1
            metrics.status = ProviderHealthStatus.PAUSED
            metrics.cooldown_until = now + 300.0
            cls._sync_profile_health(provider, ProviderHealthStatus.PAUSED)
            logger.warning(f"[HealthMonitor] Provider '{provider}' model/endpoint NOT FOUND (404). Auto-paused.")

        elif status_code == 429 or any(k in err_lower for k in ["ratelimit", "rate limit", "quota", "daily limit", "billing"]):
            metrics.count_429 += 1
            metrics.status = ProviderHealthStatus.COOLDOWN
            multiplier = min(2 ** (metrics.consecutive_failures - 1), 4)
            duration = cooldown_seconds * multiplier
            metrics.cooldown_until = now + duration
            cls._sync_profile_health(provider, ProviderHealthStatus.COOLDOWN)
            logger.warning(f"[HealthMonitor] Provider '{provider}' RATE LIMITED (429/quota). Cooldown for {duration}s.")

        elif status_code == 408 or "timeout" in err_lower:
            metrics.count_timeout += 1
            metrics.status = ProviderHealthStatus.COOLDOWN
            metrics.cooldown_until = now + 30.0
            cls._sync_profile_health(provider, ProviderHealthStatus.COOLDOWN)
            logger.warning(f"[HealthMonitor] Provider '{provider}' TIMED OUT (408). Cooldown for 30s.")

        elif status_code in (500, 502, 503, 504) or any(k in err_lower for k in ["connection", "refused", "ssl", "dns", "network", "unavailable"]):
            metrics.status = ProviderHealthStatus.OFFLINE
            metrics.cooldown_until = now + 60.0
            cls._sync_profile_health(provider, ProviderHealthStatus.OFFLINE)
            logger.warning(f"[HealthMonitor] Provider '{provider}' OFFLINE/Network error ({error_type}). Cooldown for 60s.")

        else:
            if metrics.consecutive_failures >= 3:
                metrics.status = ProviderHealthStatus.COOLDOWN
                metrics.cooldown_until = now + 30.0
                cls._sync_profile_health(provider, ProviderHealthStatus.COOLDOWN)
                logger.warning(f"[HealthMonitor] Provider '{provider}' had {metrics.consecutive_failures} consecutive failures. Cooldown for 30s.")

    @classmethod
    def get_health_snapshot(cls) -> Dict[str, Any]:
        return {k: v.model_dump() for k, v in cls._metrics_store.items()}

    @classmethod
    def reset(cls) -> None:
        cls._metrics_store.clear()
