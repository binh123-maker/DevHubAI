"""
Pipeline Registry — Phase 10.6

Central registration of stages. PipelineRunner reads exclusively from here.
Never hardcode execution order inside PipelineRunner.
"""
from __future__ import annotations
import logging
from typing import Dict, List, Optional

from app.services.pipeline.pipeline_stage import PipelineStage

logger = logging.getLogger(__name__)


class PipelineRegistry:
    """Manages stage registration and builds the default execution order."""

    _DEFAULT_ORDER = [
        "StructureAnalysisStage",
        "SemanticUnitStage",
        "BoundaryDetectionStage",
        "SemanticChunkBuilderStage",
        "ChunkScoringStage",
        "SemanticValidationStage",
        "SemanticRepairStage",
        "StoreChunkStage",
    ]

    def __init__(self) -> None:
        self._stages: Dict[str, PipelineStage] = {}
        self._order: List[str] = []

    # ------------------------------------------------------------------
    def register(self, stage: PipelineStage) -> None:
        name = stage.name()
        self._stages[name] = stage
        if name not in self._order:
            self._order.append(name)
        logger.debug("Registered stage: %s v%s", name, stage.version())

    def unregister(self, name: str) -> None:
        self._stages.pop(name, None)
        if name in self._order:
            self._order.remove(name)

    def get_stage(self, name: str) -> Optional[PipelineStage]:
        return self._stages.get(name)

    def get_registered_stages(self) -> List[PipelineStage]:
        return [self._stages[n] for n in self._order if n in self._stages]

    def registered_names(self) -> List[str]:
        return list(self._order)

    # ------------------------------------------------------------------
    def build_default_pipeline(self) -> List[PipelineStage]:
        """Register all default stages in canonical order and return them."""
        from app.services.pipeline.pipeline_stages import (
            StructureAnalysisStage,
            SemanticUnitStage,
            BoundaryDetectionStage,
            SemanticChunkBuilderStage,
            ChunkScoringStage,
            SemanticValidationStage,
            SemanticRepairStage,
            StoreChunkStage,
        )
        defaults = [
            StructureAnalysisStage(),
            SemanticUnitStage(),
            BoundaryDetectionStage(),
            SemanticChunkBuilderStage(),
            ChunkScoringStage(),
            SemanticValidationStage(),
            SemanticRepairStage(),
            StoreChunkStage(),
        ]
        for stage in defaults:
            if stage.name() not in self._stages:
                self.register(stage)
        # Respect canonical order
        stage_map = {s.name(): s for s in defaults}
        return [stage_map[n] for n in self._DEFAULT_ORDER if n in stage_map]

    # ------------------------------------------------------------------
    def validate_dependencies(self) -> List[str]:
        """Return list of dependency errors; empty list means graph is valid."""
        errors = []
        registered = set(self._stages.keys())
        seen = []
        for name in self._order:
            stage = self._stages.get(name)
            if not stage:
                continue
            for dep in stage.dependencies():
                if dep not in registered:
                    errors.append(f"Stage '{name}' requires missing stage '{dep}'")
                elif dep not in seen:
                    errors.append(f"Stage '{name}' requires '{dep}' to run first (ordering issue)")
            seen.append(name)
        # Check duplicates
        if len(self._order) != len(set(self._order)):
            errors.append("Duplicate stage names detected")
        return errors

    # ------------------------------------------------------------------
    @classmethod
    def default(cls) -> "PipelineRegistry":
        registry = cls()
        registry.build_default_pipeline()
        return registry
