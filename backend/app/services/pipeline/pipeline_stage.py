"""
Abstract PipelineStage — Phase 10.6

Base class that every processing stage must implement.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List

from app.services.pipeline.pipeline_context import PipelineContext
from app.services.pipeline.pipeline_stage_result import StageResult


class PipelineStage(ABC):
    """Abstract base for every stage in the Semantic Pipeline."""

    # -----------------------------------------------------------------
    # Required interface
    # -----------------------------------------------------------------
    @abstractmethod
    def execute(self, ctx: PipelineContext) -> StageResult:
        """Run this stage, mutate ctx outputs, return StageResult."""

    @abstractmethod
    def name(self) -> str:
        """Unique stage identifier used by registry and runner."""

    # -----------------------------------------------------------------
    # Optional overrides
    # -----------------------------------------------------------------
    def version(self) -> str:
        return "1.0"

    def dependencies(self) -> List[str]:
        """Names of stages that must execute before this one."""
        return []

    def supports(self, ctx: PipelineContext) -> bool:
        """Return False to skip this stage for the given context."""
        return True

    def rollback(self, ctx: PipelineContext) -> None:
        """Undo any mutations made during execute(). Optional."""

    def validate(self, ctx: PipelineContext) -> List[str]:
        """Pre-execution context validation. Returns list of error messages."""
        return []
