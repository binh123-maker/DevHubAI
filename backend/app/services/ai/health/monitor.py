import time
import logging
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class ProviderHealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    COOLDOWN = "COOLDOWN"
    OFFLINE = "OFFLINE"
    UNAUTHORIZED = "UNAUTHORIZED"
    DISABLED = "DISABLED"

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
    _metrics_store: Dict[str, ProviderMetrics] = {}

    @classmethod
    def _get_or_create(cls, provider: str) -> ProviderMetrics:
        key = provider.lower()
        if key not in cls._metrics_store:
            cls._metrics_store[key] = ProviderMetrics(provider_name=key)
        return cls._metrics_store[key]

    @classmethod
    def is_provider_healthy(cls, provider: str) -> bool:
        metrics = cls._get_or_create(provider)
        now = time.time()

        # Check if in cooldown
        if metrics.status == ProviderHealthStatus.COOLDOWN:
            if metrics.cooldown_until and now >= metrics.cooldown_until:
                # Cooldown expired -> automatically re-enable
                metrics.status = ProviderHealthStatus.HEALTHY
                metrics.cooldown_until = None
                logger.info(f"[HealthMonitor] Provider '{provider}' cooldown expired. Transitioned to HEALTHY.")
                return True
            return False

        if metrics.status in (ProviderHealthStatus.OFFLINE, ProviderHealthStatus.UNAUTHORIZED, ProviderHealthStatus.DISABLED):
            # Check if offline cooldown expired
            if metrics.cooldown_until and now >= metrics.cooldown_until:
                metrics.status = ProviderHealthStatus.HEALTHY
                metrics.cooldown_until = None
                return True
            return False

        return True

    @classmethod
    def record_success(cls, provider: str, latency_ms: float) -> None:
        metrics = cls._get_or_create(provider)
        metrics.total_requests += 1
        metrics.success_count += 1
        metrics.consecutive_failures = 0
        metrics.status = ProviderHealthStatus.HEALTHY
        metrics.last_success_timestamp = time.time()
        # Update rolling average latency
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
            metrics.cooldown_until = now + 3600.0  # 1 hour cooldown
            logger.warning(f"[HealthMonitor] Provider '{provider}' marked UNAUTHORIZED (401/403).")

        elif status_code == 404 or "notfound" in err_lower:
            metrics.count_404 += 1
            logger.warning(f"[HealthMonitor] Provider '{provider}' model/endpoint NOT FOUND (404).")

        elif status_code == 429 or any(k in err_lower for k in ["ratelimit", "rate limit", "quota", "daily limit", "billing"]):
            metrics.count_429 += 1
            metrics.status = ProviderHealthStatus.COOLDOWN
            multiplier = min(2 ** (metrics.consecutive_failures - 1), 4)
            metrics.cooldown_until = now + (cooldown_seconds * multiplier)
            logger.warning(f"[HealthMonitor] Provider '{provider}' RATE LIMITED (429/quota). Cooldown for {cooldown_seconds * multiplier}s.")

        elif status_code == 408 or "timeout" in err_lower:
            metrics.count_timeout += 1
            metrics.status = ProviderHealthStatus.COOLDOWN
            metrics.cooldown_until = now + 30.0
            logger.warning(f"[HealthMonitor] Provider '{provider}' TIMED OUT (408). Cooldown for 30s.")

        elif status_code in (500, 502, 503, 504) or any(k in err_lower for k in ["connection", "refused", "ssl", "dns", "network", "unavailable"]):
            metrics.status = ProviderHealthStatus.OFFLINE
            metrics.cooldown_until = now + 60.0
            logger.warning(f"[HealthMonitor] Provider '{provider}' OFFLINE/Network error ({error_type}). Cooldown for 60s.")

        else:
            if metrics.consecutive_failures >= 3:
                metrics.status = ProviderHealthStatus.COOLDOWN
                metrics.cooldown_until = now + 30.0
                logger.warning(f"[HealthMonitor] Provider '{provider}' had {metrics.consecutive_failures} consecutive failures. Cooldown for 30s.")

    @classmethod
    def get_health_snapshot(cls) -> Dict[str, Any]:
        return {k: v.model_dump() for k, v in cls._metrics_store.items()}

    @classmethod
    def reset(cls) -> None:
        cls._metrics_store.clear()
