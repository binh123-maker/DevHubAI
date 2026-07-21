"""
Pipeline Runner — Phase 10.6

Orchestrates stage execution with dependency validation, retry, rollback,
hooks, and event emission.
"""
from __future__ import annotations
import logging
import time
from typing import List, Optional

from app.services.pipeline.pipeline_context import PipelineContext
from app.services.pipeline.pipeline_profile import PipelineProfile
from app.services.pipeline.pipeline_registry import PipelineRegistry
from app.services.pipeline.pipeline_retry import RetryPolicy
from app.services.pipeline.pipeline_hooks import PipelineHooks
from app.services.pipeline.pipeline_stage_result import StageResult
from app.services.pipeline.pipeline_events import (
    StageStarted, StageFinished, StageFailed,
    RollbackStarted, RollbackFinished, StageRetrying,
    DependencyValidationFailed,
)

logger = logging.getLogger(__name__)


class PipelineRunner:
    """Executes registered stages in order with full observability."""

    def __init__(
        self,
        registry: PipelineRegistry,
        profile: Optional[PipelineProfile] = None,
        retry_policy: Optional[RetryPolicy] = None,
        hooks: Optional[PipelineHooks] = None,
    ) -> None:
        self.registry = registry
        self.profile = profile or PipelineProfile.production()
        self.retry_policy = retry_policy or RetryPolicy(
            max_retries=self.profile.max_retries,
            retry_delay=self.profile.retry_delay,
            exponential_backoff=self.profile.exponential_backoff,
        )
        self.hooks = hooks or PipelineHooks()
        self._stage_results: dict = {}

    # ------------------------------------------------------------------
    def validate_dependencies(self, ctx: PipelineContext) -> List[str]:
        errors = self.registry.validate_dependencies()
        for err in errors:
            ctx.emit_event(DependencyValidationFailed(ctx.pipeline_id, err))
            logger.error("Dependency error: %s", err)
        return errors

    # ------------------------------------------------------------------
    def run(self, ctx: PipelineContext) -> List[StageResult]:
        """Execute all registered stages in order. Returns list of results."""
        results: List[StageResult] = []
        stages = self.registry.get_registered_stages()

        for stage in stages:
            stage_name = stage.name()

            # Profile-driven skip
            skip_flag = f"enable_{stage_name.lower().replace('stage', '').strip('_')}"
            if not getattr(self.profile, skip_flag, True):
                logger.debug("Skipping stage %s (disabled by profile)", stage_name)
                continue

            # Supports check
            if not stage.supports(ctx):
                logger.debug("Skipping stage %s (supports() returned False)", stage_name)
                result = StageResult(stage_name=stage_name, success=True)
                result.add_warning("Stage skipped: supports() returned False")
                self._stage_results[stage_name] = result
                results.append(result)
                continue

            # Hooks
            self.hooks.fire_before_stage(ctx, stage_name)
            ctx.emit_event(StageStarted(ctx.pipeline_id, stage_name))

            t0 = time.time()
            result = self._execute_stage(ctx, stage)
            elapsed = time.time() - t0
            result.execution_time = elapsed

            ctx.record_stage(stage_name, elapsed, result.success)
            self._stage_results[stage_name] = result
            results.append(result)

            if result.success:
                ctx.emit_event(StageFinished(ctx.pipeline_id, stage_name, elapsed, True))
                self.hooks.fire_after_stage(ctx, stage_name, result)
            else:
                ctx.emit_event(StageFailed(ctx.pipeline_id, stage_name, "; ".join(result.errors)))
                self.hooks.fire_on_stage_failure(ctx, stage_name, "; ".join(result.errors))
                if result.rollback_required:
                    self._rollback(ctx, stage)

                # Critical stages abort the pipeline
                if stage_name in ("SemanticChunkBuilderStage",):
                    logger.error("Critical stage %s failed. Aborting semantic pipeline.", stage_name)
                    raise RuntimeError(f"Critical stage failed: {stage_name}: {result.errors}")

        return results

    # ------------------------------------------------------------------
    def _execute_stage(self, ctx: PipelineContext, stage) -> StageResult:
        attempt = 0
        while True:
            try:
                return stage.execute(ctx)
            except Exception as exc:
                if self.retry_policy.should_retry(exc, attempt):
                    delay = self.retry_policy.delay_for(attempt)
                    ctx.emit_event(StageRetrying(ctx.pipeline_id, stage.name(), attempt + 1))
                    self.retry_policy.total_retries += 1
                    logger.warning("Retrying stage %s (attempt %d): %s", stage.name(), attempt + 1, exc)
                    time.sleep(delay)
                    attempt += 1
                else:
                    r = StageResult(stage_name=stage.name(), success=False)
                    r.add_error(str(exc))
                    return r

    # ------------------------------------------------------------------
    def _rollback(self, ctx: PipelineContext, stage) -> None:
        ctx.emit_event(RollbackStarted(ctx.pipeline_id, stage.name()))
        try:
            stage.rollback(ctx)
        except Exception as exc:
            logger.warning("Rollback of %s failed: %s", stage.name(), exc)
        ctx.emit_event(RollbackFinished(ctx.pipeline_id, stage.name()))

    # ------------------------------------------------------------------
    @property
    def stage_results(self) -> dict:
        return dict(self._stage_results)
