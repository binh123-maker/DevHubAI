"""
Pipeline Health Monitor — Phase 10.6

Computes overall pipeline health from metrics and statistics.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any


class HealthLevel(str, Enum):
    HEALTHY  = "HEALTHY"
    WARNING  = "WARNING"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"


@dataclass
class PipelineHealth:
    """Snapshot of pipeline health computed from live metrics."""

    success_rate: float = 1.0
    failure_rate: float = 0.0
    fallback_rate: float = 0.0
    repair_rate: float = 0.0
    validation_rate: float = 1.0
    average_execution_time: float = 0.0
    average_chunk_throughput: float = 0.0
    average_stage_latency: float = 0.0

    @property
    def health_score(self) -> float:
        score = (
            self.success_rate * 0.40
            + (1.0 - self.failure_rate) * 0.25
            + (1.0 - self.fallback_rate) * 0.20
            + self.validation_rate * 0.15
        )
        return round(min(1.0, max(0.0, score)), 3)

    @property
    def level(self) -> HealthLevel:
        s = self.health_score
        if s >= 0.90:
            return HealthLevel.HEALTHY
        if s >= 0.70:
            return HealthLevel.WARNING
        if s >= 0.50:
            return HealthLevel.DEGRADED
        return HealthLevel.CRITICAL

    @property
    def is_healthy(self) -> bool:
        return self.level in (HealthLevel.HEALTHY, HealthLevel.WARNING)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "health_score": self.health_score,
            "level": self.level.value,
            "success_rate": self.success_rate,
            "failure_rate": self.failure_rate,
            "fallback_rate": self.fallback_rate,
            "repair_rate": self.repair_rate,
            "validation_rate": self.validation_rate,
            "average_execution_time": self.average_execution_time,
            "average_chunk_throughput": self.average_chunk_throughput,
        }

    @classmethod
    def from_metrics(cls, metrics: Any, statistics: Any) -> "PipelineHealth":
        """Compute a PipelineHealth from PipelineMetrics + PipelineStatistics."""
        n = getattr(metrics, "documents_processed", 0) or 1
        return cls(
            success_rate=getattr(metrics, "success_rate", 1.0),
            failure_rate=getattr(metrics, "failed_pipelines", 0) / n,
            fallback_rate=getattr(metrics, "fallback_rate", 0.0),
            repair_rate=getattr(statistics, "repair_count", 0) / max(1, getattr(statistics, "documents_processed", 1)),
            validation_rate=getattr(statistics, "validation_passed", 0) / max(1, getattr(statistics, "validation_count", 1)),
            average_execution_time=getattr(metrics, "average_execution_time", 0.0),
            average_chunk_throughput=getattr(statistics, "average_chunks", 0.0),
        )
