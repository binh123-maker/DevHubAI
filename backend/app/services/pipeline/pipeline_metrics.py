"""
Pipeline Metrics — Phase 10.6

Tracks pipeline-level counters and throughput.
"""
from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class PipelineMetrics:
    """Aggregate counters for the pipeline orchestration layer."""

    documents_processed: int = 0
    successful_pipelines: int = 0
    failed_pipelines: int = 0
    fallback_pipelines: int = 0
    total_execution_time: float = 0.0
    stage_execution_times: Dict[str, float] = field(default_factory=dict)

    # Extended Phase 10.6 fields
    peak_memory: float = 0.0
    peak_chunk_count: int = 0
    peak_execution_time: float = 0.0
    retry_count: int = 0
    rollback_count: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    event_count: int = 0
    plugin_count: int = 0

    # ------------------------------------------------------------------
    def record_success(self, elapsed: float) -> None:
        self.documents_processed += 1
        self.successful_pipelines += 1
        self.total_execution_time += elapsed
        if elapsed > self.peak_execution_time:
            self.peak_execution_time = elapsed

    def record_failure(self, elapsed: float) -> None:
        self.documents_processed += 1
        self.failed_pipelines += 1
        self.total_execution_time += elapsed

    def record_fallback(self) -> None:
        self.fallback_pipelines += 1

    def record_stage_time(self, stage: str, elapsed: float) -> None:
        if stage not in self.stage_execution_times:
            self.stage_execution_times[stage] = 0.0
        self.stage_execution_times[stage] += elapsed

    def record_chunk_count(self, count: int) -> None:
        if count > self.peak_chunk_count:
            self.peak_chunk_count = count

    @property
    def average_execution_time(self) -> float:
        if self.documents_processed == 0:
            return 0.0
        return self.total_execution_time / self.documents_processed

    @property
    def success_rate(self) -> float:
        if self.documents_processed == 0:
            return 1.0
        return self.successful_pipelines / self.documents_processed

    @property
    def fallback_rate(self) -> float:
        if self.documents_processed == 0:
            return 0.0
        return self.fallback_pipelines / self.documents_processed

    def to_dict(self) -> Dict[str, Any]:
        return {
            "documents_processed": self.documents_processed,
            "successful_pipelines": self.successful_pipelines,
            "failed_pipelines": self.failed_pipelines,
            "fallback_pipelines": self.fallback_pipelines,
            "average_execution_time": self.average_execution_time,
            "peak_execution_time": self.peak_execution_time,
            "peak_chunk_count": self.peak_chunk_count,
            "success_rate": self.success_rate,
            "fallback_rate": self.fallback_rate,
            "retry_count": self.retry_count,
            "rollback_count": self.rollback_count,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "event_count": self.event_count,
            "plugin_count": self.plugin_count,
            "stage_execution_times": self.stage_execution_times,
        }
