"""
Pipeline Context — Phase 10.6

Shared runtime state carried across every pipeline stage.
"""
from __future__ import annotations
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PipelineContext:
    """Mutable state container shared across all PipelineStage instances."""

    # Identity
    pipeline_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    pipeline_version: str = "1.0.0"
    pipeline_run: int = 0

    # Document inputs
    document: Any = None
    document_version: Any = None
    nodes: List[Any] = field(default_factory=list)

    # Stage outputs
    semantic_units: List[Any] = field(default_factory=list)
    boundaries: List[Any] = field(default_factory=list)
    chunks: List[Any] = field(default_factory=list)
    scores: List[Any] = field(default_factory=list)
    validation_result: Optional[Any] = None
    repair_result: Optional[Any] = None
    revalidation_result: Optional[Any] = None
    repaired_chunk_ids: set = field(default_factory=set)

    # ORM chunks for persistence
    db_chunks: List[Dict[str, Any]] = field(default_factory=list)

    # Pipeline state
    fallback_used: bool = False
    pipeline_health: float = 1.0
    pipeline_status: str = "PENDING"
    start_time: float = field(default_factory=time.time)
    end_time: float = 0.0

    # Instrumentation
    metrics: Dict[str, Any] = field(default_factory=dict)
    statistics: Dict[str, Any] = field(default_factory=dict)
    events: List[Any] = field(default_factory=list)
    stage_timings: Dict[str, float] = field(default_factory=dict)
    stage_results: Dict[str, Any] = field(default_factory=dict)
    execution_trace: List[Dict[str, Any]] = field(default_factory=list)
    configuration: Dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    def record_stage(self, stage_name: str, elapsed: float, success: bool) -> None:
        self.stage_timings[stage_name] = elapsed
        self.execution_trace.append({
            "stage": stage_name,
            "elapsed": elapsed,
            "success": success,
            "timestamp": time.time(),
        })

    def emit_event(self, event: Any) -> None:
        self.events.append(event)

    def total_elapsed(self) -> float:
        end = self.end_time or time.time()
        return end - self.start_time

    def summary(self) -> Dict[str, Any]:
        return {
            "pipeline_id": self.pipeline_id,
            "pipeline_version": self.pipeline_version,
            "pipeline_status": self.pipeline_status,
            "pipeline_health": self.pipeline_health,
            "fallback_used": self.fallback_used,
            "chunks": len(self.chunks),
            "scores": len(self.scores),
            "stage_timings": self.stage_timings,
            "total_elapsed": self.total_elapsed(),
        }
