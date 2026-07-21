"""
Pipeline Statistics — Phase 10.6

Collects chunk/score/validation/repair statistics per pipeline run.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class PipelineStatistics:
    """Per-run statistics collected during pipeline execution."""

    # Volume counters
    documents_processed: int = 0
    successful_documents: int = 0
    failed_documents: int = 0
    fallback_documents: int = 0

    # Chunk stats
    total_chunks: int = 0
    chunks_per_run: List[int] = field(default_factory=list)

    # Score stats
    total_scores: int = 0
    score_values: List[float] = field(default_factory=list)

    # Validation stats
    validation_count: int = 0
    validation_passed: int = 0
    validation_failed: int = 0

    # Repair stats
    repair_count: int = 0
    repair_success: int = 0
    repair_failed: int = 0

    # Timing
    stage_latencies: Dict[str, List[float]] = field(default_factory=dict)
    pipeline_latencies: List[float] = field(default_factory=list)

    # Stage counts
    pipeline_stage_count: int = 0
    fallback_count: int = 0

    # ------------------------------------------------------------------
    def record_run(
        self, *,
        chunks: int,
        scores: List[float],
        validation_passed: bool,
        repair_performed: bool,
        repair_succeeded: bool,
        elapsed: float,
        fallback: bool = False,
        success: bool = True
    ) -> None:
        self.documents_processed += 1
        if success:
            self.successful_documents += 1
        else:
            self.failed_documents += 1
        if fallback:
            self.fallback_documents += 1
            self.fallback_count += 1

        self.total_chunks += chunks
        self.chunks_per_run.append(chunks)

        self.score_values.extend(scores)
        self.total_scores += len(scores)

        self.validation_count += 1
        if validation_passed:
            self.validation_passed += 1
        else:
            self.validation_failed += 1

        if repair_performed:
            self.repair_count += 1
            if repair_succeeded:
                self.repair_success += 1
            else:
                self.repair_failed += 1

        self.pipeline_latencies.append(elapsed)

    def record_stage_latency(self, stage: str, elapsed: float) -> None:
        if stage not in self.stage_latencies:
            self.stage_latencies[stage] = []
        self.stage_latencies[stage].append(elapsed)

    # ------------------------------------------------------------------
    @property
    def average_chunks(self) -> float:
        if not self.chunks_per_run:
            return 0.0
        return sum(self.chunks_per_run) / len(self.chunks_per_run)

    @property
    def average_score(self) -> float:
        if not self.score_values:
            return 0.0
        return sum(self.score_values) / len(self.score_values)

    @property
    def average_latency(self) -> float:
        if not self.pipeline_latencies:
            return 0.0
        return sum(self.pipeline_latencies) / len(self.pipeline_latencies)

    @property
    def pipeline_success_rate(self) -> float:
        if self.documents_processed == 0:
            return 1.0
        return self.successful_documents / self.documents_processed

    def average_stage_latency(self, stage: str) -> float:
        vals = self.stage_latencies.get(stage, [])
        if not vals:
            return 0.0
        return sum(vals) / len(vals)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "documents_processed": self.documents_processed,
            "successful_documents": self.successful_documents,
            "failed_documents": self.failed_documents,
            "fallback_documents": self.fallback_documents,
            "total_chunks": self.total_chunks,
            "average_chunks_per_document": self.average_chunks,
            "average_scores": self.average_score,
            "validation_count": self.validation_count,
            "validation_passed": self.validation_passed,
            "validation_failed": self.validation_failed,
            "repair_count": self.repair_count,
            "repair_success": self.repair_success,
            "repair_failed": self.repair_failed,
            "average_stage_time": {s: self.average_stage_latency(s) for s in self.stage_latencies},
            "average_pipeline_time": self.average_latency,
            "pipeline_success_rate": self.pipeline_success_rate,
            "fallback_count": self.fallback_count,
        }
