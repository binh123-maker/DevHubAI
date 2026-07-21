"""
Phase 10.6 Pipeline Framework Tests

Covers: Registry, Dependency Validation, StageResult, PipelineProfile,
Retry, Hooks, Health, Manifest, Graph, Replay, Plugin, Statistics,
Metrics, Reports, Full Execution, Legacy Fallback, Backward Compatibility.
"""
import pytest
from app.services.pipeline.pipeline_context import PipelineContext
from app.services.pipeline.pipeline_stage import PipelineStage
from app.services.pipeline.pipeline_stage_result import StageResult
from app.services.pipeline.pipeline_profile import PipelineProfile
from app.services.pipeline.pipeline_registry import PipelineRegistry
from app.services.pipeline.pipeline_runner import PipelineRunner
from app.services.pipeline.pipeline_retry import RetryPolicy
from app.services.pipeline.pipeline_hooks import PipelineHooks
from app.services.pipeline.pipeline_metrics import PipelineMetrics
from app.services.pipeline.pipeline_statistics import PipelineStatistics
from app.services.pipeline.pipeline_health import PipelineHealth, HealthLevel
from app.services.pipeline.pipeline_manifest import PipelineManifest, StageManifestEntry
from app.services.pipeline.pipeline_graph import PipelineGraph
from app.services.pipeline.pipeline_replay_player import PipelineReplayPlayer
from app.services.pipeline.pipeline_explanation_report import PipelineExplanationReport
from app.services.pipeline.pipeline_plugin import PipelinePlugin, PipelinePluginRegistry, PluginManifest
from app.services.pipeline.pipeline_events import (
    PipelineStarted, PipelineFinished, StageStarted, StageFinished,
    StageFailed, FallbackActivated,
)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
class AlwaysPassStage(PipelineStage):
    def __init__(self, stage_name="AlwaysPass", deps=None):
        self._name = stage_name
        self._deps = deps or []

    def name(self): return self._name
    def dependencies(self): return self._deps

    def execute(self, ctx):
        r = StageResult(stage_name=self._name)
        r.add_output("ok", True)
        return r


class AlwaysFailStage(PipelineStage):
    def name(self): return "AlwaysFailStage"

    def execute(self, ctx):
        raise ValueError("Permanent failure")


class SkipStage(PipelineStage):
    def name(self): return "SkipStage"
    def supports(self, ctx): return False

    def execute(self, ctx):
        return StageResult(stage_name=self.name())


# ─────────────────────────────────────────────────────────────────────────────
# 1. Registry
# ─────────────────────────────────────────────────────────────────────────────
class TestPipelineRegistry:
    def test_register_and_get(self):
        reg = PipelineRegistry()
        stage = AlwaysPassStage("TestStage")
        reg.register(stage)
        assert reg.get_stage("TestStage") is stage

    def test_unregister(self):
        reg = PipelineRegistry()
        reg.register(AlwaysPassStage("RemoveMe"))
        reg.unregister("RemoveMe")
        assert reg.get_stage("RemoveMe") is None

    def test_registered_names_order(self):
        reg = PipelineRegistry()
        for name in ["A", "B", "C"]:
            reg.register(AlwaysPassStage(name))
        assert reg.registered_names() == ["A", "B", "C"]

    def test_build_default_pipeline_returns_8_stages(self):
        reg = PipelineRegistry()
        stages = reg.build_default_pipeline()
        assert len(stages) == 8

    def test_default_factory(self):
        reg = PipelineRegistry.default()
        assert len(reg.get_registered_stages()) == 8


# ─────────────────────────────────────────────────────────────────────────────
# 2. Dependency Validation
# ─────────────────────────────────────────────────────────────────────────────
class TestDependencyValidation:
    def test_valid_dependency_graph_returns_no_errors(self):
        reg = PipelineRegistry()
        reg.register(AlwaysPassStage("A", deps=[]))
        reg.register(AlwaysPassStage("B", deps=["A"]))
        errors = reg.validate_dependencies()
        assert errors == []

    def test_missing_dependency_detected(self):
        reg = PipelineRegistry()
        reg.register(AlwaysPassStage("B", deps=["Missing"]))
        errors = reg.validate_dependencies()
        assert any("Missing" in e for e in errors)

    def test_ordering_error_detected(self):
        reg = PipelineRegistry()
        # B depends on A but A is registered after B
        reg.register(AlwaysPassStage("B", deps=["A"]))
        reg.register(AlwaysPassStage("A", deps=[]))
        errors = reg.validate_dependencies()
        # B requires A to run first — ordering error
        assert any("B" in e for e in errors)


# ─────────────────────────────────────────────────────────────────────────────
# 3. StageResult
# ─────────────────────────────────────────────────────────────────────────────
class TestStageResult:
    def test_default_is_success(self):
        r = StageResult(stage_name="Test")
        assert r.success is True
        assert not r.has_errors

    def test_add_error_marks_failure(self):
        r = StageResult(stage_name="Test")
        r.add_error("oops")
        assert r.success is False
        assert r.has_errors

    def test_add_warning_does_not_fail(self):
        r = StageResult(stage_name="Test")
        r.add_warning("careful")
        assert r.success is True
        assert r.has_warnings

    def test_to_dict(self):
        r = StageResult(stage_name="Test", stage_version="2.0")
        d = r.to_dict()
        assert d["stage_name"] == "Test"
        assert d["stage_version"] == "2.0"


# ─────────────────────────────────────────────────────────────────────────────
# 4. PipelineProfile
# ─────────────────────────────────────────────────────────────────────────────
class TestPipelineProfile:
    def test_production_preset(self):
        p = PipelineProfile.production()
        assert p.profile_name == "production"
        assert p.enable_fallback is True
        assert p.enable_graph is False

    def test_debug_preset_enables_graph(self):
        p = PipelineProfile.debug()
        assert p.enable_graph is True
        assert p.enable_reports is True

    def test_testing_preset_disables_cache(self):
        p = PipelineProfile.testing()
        assert p.enable_cache is False

    def test_to_dict(self):
        d = PipelineProfile.production().to_dict()
        assert "profile_name" in d
        assert "pipeline_version" in d


# ─────────────────────────────────────────────────────────────────────────────
# 5. Retry Policy
# ─────────────────────────────────────────────────────────────────────────────
class TestRetryPolicy:
    def test_permanent_exception_not_retried(self):
        policy = RetryPolicy(max_retries=3)
        assert policy.should_retry(ValueError("perm"), 0) is False

    def test_transient_exception_retried(self):
        policy = RetryPolicy(max_retries=3)
        assert policy.should_retry(RuntimeError("transient"), 0) is True

    def test_exhausted_retries_not_retried(self):
        policy = RetryPolicy(max_retries=2)
        assert policy.should_retry(RuntimeError("trans"), 2) is False

    def test_exponential_backoff_grows(self):
        p = RetryPolicy(retry_delay=0.1, backoff_multiplier=2.0)
        assert p.delay_for(1) > p.delay_for(0)

    def test_no_retry_factory(self):
        p = RetryPolicy.no_retry()
        assert p.max_retries == 0

    def test_statistics_structure(self):
        p = RetryPolicy()
        s = p.statistics()
        assert "total_retries" in s


# ─────────────────────────────────────────────────────────────────────────────
# 6. Hooks
# ─────────────────────────────────────────────────────────────────────────────
class TestPipelineHooks:
    def test_hook_fires_on_event(self):
        fired = []
        hooks = PipelineHooks()
        hooks.register_before_pipeline(lambda ctx: fired.append("bp"))
        hooks.fire_before_pipeline(ctx=None)
        assert "bp" in fired

    def test_hook_error_does_not_raise(self):
        hooks = PipelineHooks()
        hooks.register_before_pipeline(lambda ctx: (_ for _ in ()).throw(RuntimeError("boom")))
        # Should not raise
        hooks.fire_before_pipeline(ctx=None)

    def test_summary_counts(self):
        hooks = PipelineHooks()
        hooks.register_after_stage(lambda **kw: None)
        hooks.register_after_stage(lambda **kw: None)
        s = hooks.summary()
        assert s["after_stage"] == 2


# ─────────────────────────────────────────────────────────────────────────────
# 7. Health Monitor
# ─────────────────────────────────────────────────────────────────────────────
class TestPipelineHealth:
    def test_full_success_is_healthy(self):
        h = PipelineHealth(success_rate=1.0, failure_rate=0.0, fallback_rate=0.0, validation_rate=1.0)
        assert h.level == HealthLevel.HEALTHY

    def test_high_failure_is_critical(self):
        h = PipelineHealth(success_rate=0.1, failure_rate=0.9, fallback_rate=0.5, validation_rate=0.2)
        assert h.level in (HealthLevel.DEGRADED, HealthLevel.CRITICAL)

    def test_to_dict_has_level(self):
        h = PipelineHealth()
        d = h.to_dict()
        assert "level" in d
        assert "health_score" in d


# ─────────────────────────────────────────────────────────────────────────────
# 8. Manifest
# ─────────────────────────────────────────────────────────────────────────────
class TestPipelineManifest:
    def test_fingerprint_is_deterministic(self):
        m = PipelineManifest(pipeline_version="1.0.0", execution_order=["A", "B"])
        fp1 = m.compute_fingerprint()
        fp2 = m.compute_fingerprint()
        assert fp1 == fp2

    def test_to_json_is_valid(self):
        import json
        m = PipelineManifest(pipeline_version="1.0.0", stages=[
            StageManifestEntry("S1", "1.0", [], True)
        ])
        m.compute_fingerprint()
        m.compute_execution_hash()
        j = json.loads(m.to_json())
        assert j["pipeline_version"] == "1.0.0"

    def test_to_markdown_contains_title(self):
        m = PipelineManifest()
        m.compute_fingerprint()
        md = m.to_markdown()
        assert "Pipeline Manifest" in md


# ─────────────────────────────────────────────────────────────────────────────
# 9. Graph
# ─────────────────────────────────────────────────────────────────────────────
class TestPipelineGraph:
    def test_mermaid_contains_graph_td(self):
        g = PipelineGraph.from_execution_order(["A", "B", "C"])
        m = g.to_mermaid()
        assert "graph TD" in m
        assert "A" in m

    def test_graphviz_contains_digraph(self):
        g = PipelineGraph.from_execution_order(["A", "B"])
        gv = g.to_graphviz()
        assert "digraph" in gv

    def test_json_export(self):
        import json
        g = PipelineGraph.from_execution_order(["X", "Y"])
        d = json.loads(g.to_json())
        assert len(d["nodes"]) == 2
        assert len(d["edges"]) == 1


# ─────────────────────────────────────────────────────────────────────────────
# 10. Replay
# ─────────────────────────────────────────────────────────────────────────────
class TestPipelineReplayPlayer:
    def _player(self):
        trace = [
            {"stage": "A", "elapsed": 0.1, "success": True, "timestamp": 1.0},
            {"stage": "B", "elapsed": 0.2, "success": True, "timestamp": 2.0},
            {"stage": "C", "elapsed": 0.05, "success": False, "timestamp": 3.0},
        ]
        return PipelineReplayPlayer(trace)

    def test_next_advances_cursor(self):
        p = self._player()
        f = p.next()
        assert f.stage == "A"
        f = p.next()
        assert f.stage == "B"

    def test_previous_goes_back(self):
        p = self._player()
        p.next(); p.next()
        f = p.previous()
        assert f.stage == "A"

    def test_jump_to_frame(self):
        p = self._player()
        f = p.jump(2)
        assert f.stage == "C"

    def test_filter_failures(self):
        p = self._player()
        fails = p.filter_failures()
        assert len(fails) == 1
        assert fails[0].stage == "C"

    def test_timeline_export(self):
        p = self._player()
        t = p.export_timeline()
        assert "Pipeline Replay Timeline" in t

    def test_pause_stops_next(self):
        p = self._player()
        p.pause()
        assert p.next() is None


# ─────────────────────────────────────────────────────────────────────────────
# 11. Plugin
# ─────────────────────────────────────────────────────────────────────────────
class TestPipelinePlugin:
    def test_register_plugin(self):
        class TestPlugin(PipelinePlugin):
            def manifest(self):
                return PluginManifest(name="TestPlugin", version="1.0")

        reg = PipelinePluginRegistry()
        reg.register(TestPlugin())
        assert reg.is_registered("TestPlugin")
        assert reg.plugin_count() == 1

    def test_unregister_plugin(self):
        class MyPlugin(PipelinePlugin):
            def manifest(self):
                return PluginManifest(name="MyPlugin")

        reg = PipelinePluginRegistry()
        reg.register(MyPlugin())
        reg.unregister("MyPlugin")
        assert not reg.is_registered("MyPlugin")

    def test_list_plugins(self):
        reg = PipelinePluginRegistry()
        assert isinstance(reg.list_plugins(), list)

    def test_to_dict(self):
        reg = PipelinePluginRegistry()
        d = reg.to_dict()
        assert "plugin_count" in d


# ─────────────────────────────────────────────────────────────────────────────
# 12. Statistics
# ─────────────────────────────────────────────────────────────────────────────
class TestPipelineStatistics:
    def test_record_run(self):
        s = PipelineStatistics()
        s.record_run(
            chunks=10, scores=[0.8, 0.9],
            validation_passed=True, repair_performed=False,
            repair_succeeded=False, elapsed=1.0
        )
        assert s.documents_processed == 1
        assert s.total_chunks == 10

    def test_average_chunks(self):
        s = PipelineStatistics()
        s.record_run(chunks=5, scores=[], validation_passed=True,
                     repair_performed=False, repair_succeeded=False, elapsed=0.5)
        s.record_run(chunks=15, scores=[], validation_passed=True,
                     repair_performed=False, repair_succeeded=False, elapsed=0.5)
        assert s.average_chunks == 10.0

    def test_success_rate(self):
        s = PipelineStatistics()
        s.record_run(chunks=1, scores=[], validation_passed=True,
                     repair_performed=False, repair_succeeded=False, elapsed=0.1, success=True)
        s.record_run(chunks=1, scores=[], validation_passed=True,
                     repair_performed=False, repair_succeeded=False, elapsed=0.1, success=False)
        assert s.pipeline_success_rate == 0.5

    def test_to_dict_keys(self):
        s = PipelineStatistics()
        d = s.to_dict()
        assert "pipeline_success_rate" in d
        assert "average_chunks_per_document" in d


# ─────────────────────────────────────────────────────────────────────────────
# 13. Metrics
# ─────────────────────────────────────────────────────────────────────────────
class TestPipelineMetrics:
    def test_record_success(self):
        m = PipelineMetrics()
        m.record_success(1.5)
        assert m.successful_pipelines == 1
        assert m.documents_processed == 1

    def test_record_fallback(self):
        m = PipelineMetrics()
        m.record_fallback()
        assert m.fallback_pipelines == 1

    def test_average_execution_time(self):
        m = PipelineMetrics()
        m.record_success(1.0)
        m.record_success(3.0)
        assert m.average_execution_time == 2.0

    def test_to_dict_keys(self):
        m = PipelineMetrics()
        d = m.to_dict()
        assert "success_rate" in d
        assert "retry_count" in d


# ─────────────────────────────────────────────────────────────────────────────
# 14. Reports
# ─────────────────────────────────────────────────────────────────────────────
class TestPipelineExplanationReport:
    def _ctx(self):
        ctx = PipelineContext()
        ctx.pipeline_id = "test-id"
        ctx.pipeline_status = "COMPLETED"
        ctx.pipeline_health = 0.95
        ctx.stage_timings = {"StageA": 0.1, "StageB": 0.2}
        ctx.chunks = [1, 2, 3]
        ctx.scores = [1, 2]
        ctx.events = []
        return ctx

    def test_markdown_contains_header(self):
        r = PipelineExplanationReport(self._ctx())
        md = r.to_markdown()
        assert "Pipeline Execution Report" in md

    def test_json_valid(self):
        import json
        r = PipelineExplanationReport(self._ctx())
        d = json.loads(r.to_json())
        assert d["pipeline_status"] == "COMPLETED"

    def test_html_contains_html_tag(self):
        r = PipelineExplanationReport(self._ctx())
        html = r.to_html()
        assert "<html>" in html

    def test_pretty_print(self):
        r = PipelineExplanationReport(self._ctx())
        pp = r.pretty_print()
        assert "PIPELINE EXECUTION REPORT" in pp


# ─────────────────────────────────────────────────────────────────────────────
# 15. Full Pipeline Runner (unit-level with mock stages)
# ─────────────────────────────────────────────────────────────────────────────
class TestPipelineRunner:
    def test_successful_run(self):
        reg = PipelineRegistry()
        reg.register(AlwaysPassStage("S1"))
        reg.register(AlwaysPassStage("S2", deps=["S1"]))
        ctx = PipelineContext()
        runner = PipelineRunner(registry=reg, profile=PipelineProfile.testing())
        results = runner.run(ctx)
        assert all(r.success for r in results)
        assert len(results) == 2

    def test_skip_stage_on_supports_false(self):
        reg = PipelineRegistry()
        reg.register(SkipStage())
        ctx = PipelineContext()
        runner = PipelineRunner(registry=reg, profile=PipelineProfile.testing())
        results = runner.run(ctx)
        # Skipped stages still produce a result
        assert len(results) == 1
        assert results[0].has_warnings

    def test_execution_trace_populated(self):
        reg = PipelineRegistry()
        reg.register(AlwaysPassStage("X"))
        ctx = PipelineContext()
        runner = PipelineRunner(registry=reg, profile=PipelineProfile.testing())
        runner.run(ctx)
        assert len(ctx.execution_trace) == 1

    def test_events_emitted(self):
        reg = PipelineRegistry()
        reg.register(AlwaysPassStage("Y"))
        ctx = PipelineContext()
        runner = PipelineRunner(registry=reg, profile=PipelineProfile.testing())
        runner.run(ctx)
        assert any(isinstance(e, StageStarted) for e in ctx.events)


# ─────────────────────────────────────────────────────────────────────────────
# 16. Legacy Fallback
# ─────────────────────────────────────────────────────────────────────────────
class TestLegacyFallback:
    def test_chunk_builder_import(self):
        """Verify legacy builder is importable."""
        from app.services.chunk_builder import build_chunks_from_structure
        assert callable(build_chunks_from_structure)
