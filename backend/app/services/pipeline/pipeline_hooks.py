"""
Pipeline Hooks — Phase 10.6

Observable lifecycle hooks for the Semantic Pipeline.
Hooks are read-only observers — they must never modify business logic.
"""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Dict, Any

logger = logging.getLogger(__name__)

HookFn = Callable[..., None]


@dataclass
class PipelineHooks:
    """Registry of lifecycle hook callbacks."""

    _before_pipeline: List[HookFn] = field(default_factory=list)
    _after_pipeline: List[HookFn] = field(default_factory=list)
    _before_stage: List[HookFn] = field(default_factory=list)
    _after_stage: List[HookFn] = field(default_factory=list)
    _on_stage_failure: List[HookFn] = field(default_factory=list)
    _on_pipeline_failure: List[HookFn] = field(default_factory=list)
    _on_pipeline_recovered: List[HookFn] = field(default_factory=list)

    # ------------------------------------------------------------------ register
    def register_before_pipeline(self, fn: HookFn) -> None:
        self._before_pipeline.append(fn)

    def register_after_pipeline(self, fn: HookFn) -> None:
        self._after_pipeline.append(fn)

    def register_before_stage(self, fn: HookFn) -> None:
        self._before_stage.append(fn)

    def register_after_stage(self, fn: HookFn) -> None:
        self._after_stage.append(fn)

    def register_on_stage_failure(self, fn: HookFn) -> None:
        self._on_stage_failure.append(fn)

    def register_on_pipeline_failure(self, fn: HookFn) -> None:
        self._on_pipeline_failure.append(fn)

    def register_on_pipeline_recovered(self, fn: HookFn) -> None:
        self._on_pipeline_recovered.append(fn)

    # ------------------------------------------------------------------ fire
    def _fire(self, hooks: List[HookFn], **kwargs: Any) -> None:
        for fn in hooks:
            try:
                fn(**kwargs)
            except Exception as exc:
                logger.warning("Hook %s raised: %s", fn.__name__, exc)

    def fire_before_pipeline(self, ctx: Any) -> None:
        self._fire(self._before_pipeline, ctx=ctx)

    def fire_after_pipeline(self, ctx: Any) -> None:
        self._fire(self._after_pipeline, ctx=ctx)

    def fire_before_stage(self, ctx: Any, stage_name: str) -> None:
        self._fire(self._before_stage, ctx=ctx, stage_name=stage_name)

    def fire_after_stage(self, ctx: Any, stage_name: str, result: Any) -> None:
        self._fire(self._after_stage, ctx=ctx, stage_name=stage_name, result=result)

    def fire_on_stage_failure(self, ctx: Any, stage_name: str, error: str) -> None:
        self._fire(self._on_stage_failure, ctx=ctx, stage_name=stage_name, error=error)

    def fire_on_pipeline_failure(self, ctx: Any, error: str) -> None:
        self._fire(self._on_pipeline_failure, ctx=ctx, error=error)

    def fire_on_pipeline_recovered(self, ctx: Any) -> None:
        self._fire(self._on_pipeline_recovered, ctx=ctx)

    def summary(self) -> Dict[str, int]:
        return {
            "before_pipeline": len(self._before_pipeline),
            "after_pipeline": len(self._after_pipeline),
            "before_stage": len(self._before_stage),
            "after_stage": len(self._after_stage),
            "on_stage_failure": len(self._on_stage_failure),
            "on_pipeline_failure": len(self._on_pipeline_failure),
            "on_pipeline_recovered": len(self._on_pipeline_recovered),
        }
