"""
Semantic Pipeline — Phase 10.6

Top-level orchestrator. SemanticPipeline.execute() is the single entry point
called by processing_service.py.
"""
from __future__ import annotations
import logging
import time
from typing import Any, Dict, List, Optional

from app.services.pipeline.pipeline_context import PipelineContext
from app.services.pipeline.pipeline_profile import PipelineProfile
from app.services.pipeline.pipeline_registry import PipelineRegistry
from app.services.pipeline.pipeline_runner import PipelineRunner
from app.services.pipeline.pipeline_metrics import PipelineMetrics
from app.services.pipeline.pipeline_statistics import PipelineStatistics
from app.services.pipeline.pipeline_health import PipelineHealth
from app.services.pipeline.pipeline_manifest import PipelineManifest, StageManifestEntry
from app.services.pipeline.pipeline_hooks import PipelineHooks
from app.services.pipeline.pipeline_retry import RetryPolicy
from app.services.pipeline.pipeline_graph import PipelineGraph
from app.services.pipeline.pipeline_replay_player import PipelineReplayPlayer
from app.services.pipeline.pipeline_explanation_report import PipelineExplanationReport
from app.services.pipeline.pipeline_events import (
    PipelineStarted, PipelineFinished, FallbackActivated, PipelineHealthy
)

logger = logging.getLogger(__name__)

# Module-level singletons (shared across requests, not per-request)
_global_metrics = PipelineMetrics()
_global_statistics = PipelineStatistics()


class SemanticPipeline:
    """
    Production orchestration class.

    Usage (from processing_service.py):
        ctx = PipelineContext(document=doc, document_version=version, nodes=nodes)
        pipeline = SemanticPipeline(profile=PipelineProfile.production())
        pipeline.execute(ctx)
        db_chunks = ctx.db_chunks
    """

    def __init__(
        self,
        profile: Optional[PipelineProfile] = None,
        registry: Optional[PipelineRegistry] = None,
        hooks: Optional[PipelineHooks] = None,
        retry_policy: Optional[RetryPolicy] = None,
    ) -> None:
        self.profile = profile or PipelineProfile.production()
        self.registry = registry or PipelineRegistry.default()
        self.hooks = hooks or PipelineHooks()
        self.retry_policy = retry_policy or RetryPolicy(
            max_retries=self.profile.max_retries,
            retry_delay=self.profile.retry_delay,
        )
        self._runner = PipelineRunner(
            registry=self.registry,
            profile=self.profile,
            retry_policy=self.retry_policy,
            hooks=self.hooks,
        )
        self._last_ctx: Optional[PipelineContext] = None
        self._last_health: Optional[PipelineHealth] = None

    # ------------------------------------------------------------------
    def execute(self, ctx: PipelineContext) -> PipelineContext:
        """Execute the full semantic pipeline. Mutates ctx in-place."""
        self._last_ctx = ctx
        ctx.pipeline_version = self.profile.pipeline_version
        ctx.pipeline_status = "RUNNING"
        t0 = time.time()

        self.hooks.fire_before_pipeline(ctx)
        ctx.emit_event(PipelineStarted(ctx.pipeline_id, len(self.registry.get_registered_stages())))

        # Dependency validation
        dep_errors = self._runner.validate_dependencies(ctx)
        if dep_errors:
            logger.error("Dependency validation failed: %s", dep_errors)
            ctx.pipeline_status = "DEPENDENCY_ERROR"
            raise RuntimeError(f"Pipeline dependency errors: {dep_errors}")

        try:
            stage_results = self._runner.run(ctx)
            success = all(r.success for r in stage_results if r.stage_name not in ("SemanticRepairStage",))
            elapsed = time.time() - t0
            ctx.end_time = time.time()

            ctx.pipeline_health = self._compute_health(ctx)
            ctx.pipeline_status = "COMPLETED" if success else "PARTIAL"

            ctx.emit_event(PipelineFinished(ctx.pipeline_id, ctx.pipeline_health, elapsed))
            ctx.emit_event(PipelineHealthy(ctx.pipeline_id, ctx.pipeline_health))

            self.hooks.fire_after_pipeline(ctx)
            _global_metrics.record_success(elapsed)
            _global_metrics.record_chunk_count(len(ctx.chunks))
            _global_metrics.event_count += len(ctx.events)
            for sname, st in ctx.stage_timings.items():
                _global_metrics.record_stage_time(sname, st)

            _global_statistics.record_run(
                chunks=len(ctx.chunks),
                scores=[getattr(s, "overall_score", 0.0) for s in ctx.scores],
                validation_passed=bool(ctx.validation_result and not ctx.validation_result.issues),
                repair_performed=bool(ctx.repair_result),
                repair_succeeded=bool(ctx.repair_result and ctx.repair_result.repair_score > 0.5),
                elapsed=elapsed,
            )

            logger.info(
                "SemanticPipeline completed: doc=%s | chunks=%d | stages=%d | health=%.2f | elapsed=%.3fs",
                getattr(getattr(ctx, "document", None), "id", "?"),
                len(ctx.chunks), len(ctx.stage_timings), ctx.pipeline_health, elapsed
            )

        except RuntimeError:
            raise
        except Exception as exc:
            elapsed = time.time() - t0
            ctx.pipeline_status = "FAILED"
            _global_metrics.record_failure(elapsed)
            self.hooks.fire_on_pipeline_failure(ctx, str(exc))
            raise

        self._last_health = PipelineHealth.from_metrics(_global_metrics, _global_statistics)
        return ctx

    # ------------------------------------------------------------------
    def _compute_health(self, ctx: PipelineContext) -> float:
        timings = ctx.stage_timings
        if not timings:
            return 1.0
        failed = sum(
            1 for sr in self._runner.stage_results.values()
            if not getattr(sr, "success", True)
        )
        total = len(timings)
        return round(max(0.0, 1.0 - (failed / max(1, total)) * 0.5), 3)

    # ------------------------------------------------------------------
    def collect_statistics(self) -> Dict[str, Any]:
        return _global_statistics.to_dict()

    def collect_metrics(self) -> Dict[str, Any]:
        return _global_metrics.to_dict()

    def export_execution_trace(self) -> List[Dict[str, Any]]:
        if self._last_ctx:
            return self._last_ctx.execution_trace
        return []

    def build_manifest(self) -> PipelineManifest:
        stages = self.registry.get_registered_stages()
        m = PipelineManifest(
            pipeline_version=self.profile.pipeline_version,
            profile_name=self.profile.profile_name,
            stages=[
                StageManifestEntry(
                    name=s.name(),
                    version=s.version(),
                    dependencies=s.dependencies(),
                    enabled=True,
                )
                for s in stages
            ],
            execution_order=[s.name() for s in stages],
        )
        m.compute_fingerprint()
        m.compute_execution_hash()
        return m

    def build_graph(self) -> PipelineGraph:
        ctx = self._last_ctx
        sr = self._runner.stage_results if ctx else {}
        order = [s.name() for s in self.registry.get_registered_stages()]
        return PipelineGraph.from_execution_order(order, sr)

    def build_report(self) -> PipelineExplanationReport:
        return PipelineExplanationReport(
            ctx=self._last_ctx,
            metrics=_global_metrics,
            statistics=_global_statistics,
            health=self._last_health,
        )

    def build_replay(self) -> Optional[PipelineReplayPlayer]:
        if self._last_ctx:
            return PipelineReplayPlayer(self._last_ctx.execution_trace)
        return None

    @property
    def health(self) -> Optional[PipelineHealth]:
        return self._last_health
