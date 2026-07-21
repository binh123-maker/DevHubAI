"""
Stage Result — Phase 10.6

Every PipelineStage.execute() returns a StageResult (never a raw dict).
"""
from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class StageResult:
    """Typed result container returned by every PipelineStage."""
    stage_name: str
    stage_version: str = "1.0"

    # Outcome
    success: bool = True
    rollback_required: bool = False

    # Messages
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    # Timing
    execution_time: float = 0.0
    start_time: float = field(default_factory=time.time)

    # Payload
    outputs: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    statistics: Dict[str, Any] = field(default_factory=dict)
    events: List[Any] = field(default_factory=list)

    # ------------------------------------------------------------------ helpers
    @property
    def has_errors(self) -> bool:
        return bool(self.errors)

    @property
    def has_warnings(self) -> bool:
        return bool(self.warnings)

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)
        self.success = False

    def add_output(self, key: str, value: Any) -> None:
        self.outputs[key] = value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage_name": self.stage_name,
            "stage_version": self.stage_version,
            "success": self.success,
            "rollback_required": self.rollback_required,
            "warnings": self.warnings,
            "errors": self.errors,
            "execution_time": self.execution_time,
            "statistics": self.statistics,
        }
