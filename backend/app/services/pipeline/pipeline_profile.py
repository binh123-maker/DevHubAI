"""
Pipeline Profile — Phase 10.6

Feature-flag configuration for the Semantic Pipeline.
Supports production, debug, and testing presets.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class PipelineProfile:
    """Configuration profile injected into PipelineRunner."""

    profile_name: str = "production"
    pipeline_version: str = "1.0.0"

    # Stage toggles
    enable_structure_analysis: bool = True
    enable_semantic_units: bool = True
    enable_boundary_detection: bool = True
    enable_chunk_builder: bool = True
    enable_scoring: bool = True
    enable_validation: bool = True
    enable_repair: bool = True

    # Infrastructure toggles
    enable_statistics: bool = True
    enable_metrics: bool = True
    enable_cache: bool = True
    enable_events: bool = True
    enable_replay: bool = True
    enable_graph: bool = False       # off in prod (performance)
    enable_reports: bool = False     # off in prod
    enable_fallback: bool = True

    # Retry
    max_retries: int = 2
    retry_delay: float = 0.05
    exponential_backoff: bool = True

    # Quality gates
    minimum_chunk_count: int = 1
    minimum_pipeline_health: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()

    # ------------------------------------------------------------------
    # Named Presets
    # ------------------------------------------------------------------
    @classmethod
    def production(cls) -> "PipelineProfile":
        return cls(profile_name="production")

    @classmethod
    def debug(cls) -> "PipelineProfile":
        return cls(
            profile_name="debug",
            enable_graph=True,
            enable_reports=True,
            enable_replay=True,
            max_retries=1,
        )

    @classmethod
    def testing(cls) -> "PipelineProfile":
        return cls(
            profile_name="testing",
            enable_metrics=True,
            enable_statistics=True,
            enable_cache=False,     # deterministic results in tests
            enable_fallback=True,
            enable_graph=True,
            enable_reports=True,
            max_retries=0,
        )
