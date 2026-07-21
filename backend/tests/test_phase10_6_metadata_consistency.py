"""
Phase 10.6A — Metadata Consistency Tests (Revised)

Tests the build_pipeline_metadata() helper directly (unit-level)
and verifies _build_db_chunks() end-to-end consistency.

Contracts enforced:

  validation_status  : VALID | INVALID | SKIPPED  (no WARNING/FAILED)
  pipeline_status    : VALID | REPAIRED | INVALID | SKIPPED
  repair_performed   : False → repair_success must be False, repair_count == 0
  repair_success     : True  iff repair_performed=True AND repair_score > 0.5
  recommended_action : absent for VALID/SKIPPED; present and correct otherwise
  pipeline_stage_count : equals len(ctx.stage_timings)
"""
from __future__ import annotations
import pytest
from unittest.mock import MagicMock

from app.services.pipeline.pipeline_metadata_builder import (
    build_pipeline_metadata,
    _coerce_validation_status,
)
from app.services.pipeline.pipeline_context import PipelineContext
from app.services.pipeline.pipeline_stages import _build_db_chunks


# ═════════════════════════════════════════════════════════════════════════════
# Shared factories
# ═════════════════════════════════════════════════════════════════════════════

def _make_issue(severity="WARNING", description="short sentence"):
    i = MagicMock()
    i.severity = severity
    i.description = description
    return i


def _make_val_result(has_issues=False, severity="WARNING", description="short",
                     rec="Merge with next", overall_status=None):
    vr = MagicMock()
    vr.overall_validation_score = 0.8 if not has_issues else 0.5
    vr.overall_status = overall_status or ("VALID" if not has_issues else "INVALID")
    vr.issues = [_make_issue(severity, description)] if has_issues else []
    vr.recommendations = [rec] if has_issues else []
    vr.critical_count = 1 if severity == "CRITICAL" and has_issues else 0
    vr.warning_count = 1 if severity == "WARNING" and has_issues else 0
    return vr


def _make_repair_result(repair_score=0.9, repaired_chunk_ids=None):
    rr = MagicMock()
    rr.repair_score = repair_score
    rr.repair_confidence = 0.9
    rr.repair_version = "1.0"
    rr.overall_confidence = 0.9
    rr.repaired_issues = []
    for cid in (repaired_chunk_ids or []):
        ri = MagicMock()
        ri.affected_chunk = cid
        ri.confidence = 0.9
        rr.repaired_issues.append(ri)
    rr.failed_repairs = []
    return rr


def _base_kwargs(chunk_id="c1", stage_count=7):
    return dict(
        chunk_id=chunk_id,
        validation_result=None,
        repair_result=None,
        revalidation_result=None,
        repaired_chunk_ids=set(),
        stage_timings={f"Stage{i}": 0.01 for i in range(stage_count)},
        pipeline_id="pipe-test",
        pipeline_version="1.0.0",
        pipeline_health=0.95,
        fallback_used=False,
        val_profile_version="1.0",
    )


# ═════════════════════════════════════════════════════════════════════════════
# 1. _coerce_validation_status
# ═════════════════════════════════════════════════════════════════════════════
class TestCoerceValidationStatus:
    def test_valid_passthrough(self):
        assert _coerce_validation_status("VALID") == "VALID"

    def test_invalid_passthrough(self):
        assert _coerce_validation_status("INVALID") == "INVALID"

    def test_skipped_passthrough(self):
        assert _coerce_validation_status("SKIPPED") == "SKIPPED"

    def test_warning_coerced_to_invalid(self):
        assert _coerce_validation_status("WARNING") == "INVALID"

    def test_failed_coerced_to_invalid(self):
        assert _coerce_validation_status("FAILED") == "INVALID"

    def test_unknown_coerced_to_invalid(self):
        assert _coerce_validation_status("GARBAGE") == "INVALID"


# ═════════════════════════════════════════════════════════════════════════════
# 2. VALID chunk — no issues, no repair
# ═════════════════════════════════════════════════════════════════════════════
class TestValidWithoutRepair:
    def _meta(self):
        kw = _base_kwargs()
        kw["validation_result"] = _make_val_result(has_issues=False)
        return build_pipeline_metadata(**kw)

    def test_validation_status_is_valid(self):
        assert self._meta()["validation_status"] == "VALID"

    def test_pipeline_status_is_valid(self):
        assert self._meta()["pipeline_status"] == "VALID"

    def test_no_recommended_action(self):
        assert "recommended_action" not in self._meta()

    def test_repair_performed_false(self):
        assert self._meta()["repair_performed"] is False

    def test_repair_success_false(self):
        assert self._meta()["repair_success"] is False

    def test_repair_count_zero(self):
        assert self._meta()["repair_count"] == 0

    def test_repair_confidence_zero(self):
        assert self._meta()["repair_confidence"] == 0.0

    def test_no_repair_strategy_key(self):
        assert "repair_strategy" not in self._meta()

    def test_rescored_false(self):
        assert self._meta()["rescored"] is False

    def test_validation_health_above_threshold(self):
        assert self._meta()["validation_health"] == 0.8


# ═════════════════════════════════════════════════════════════════════════════
# 3. VALID after repair (REPAIRED pipeline_status)
# ═════════════════════════════════════════════════════════════════════════════
class TestValidAfterRepair:
    def _meta(self):
        kw = _base_kwargs(chunk_id="c1", stage_count=8)
        kw["validation_result"] = _make_val_result(has_issues=True, severity="WARNING")
        kw["revalidation_result"] = _make_val_result(has_issues=False)  # passed after repair
        kw["repair_result"] = _make_repair_result(repair_score=0.9, repaired_chunk_ids=["c1"])
        kw["repaired_chunk_ids"] = {"c1"}
        return build_pipeline_metadata(**kw)

    def test_pipeline_status_repaired(self):
        assert self._meta()["pipeline_status"] == "REPAIRED"

    def test_validation_status_valid(self):
        # After repair, effective_val = revalidation_result which has no issues
        assert self._meta()["validation_status"] == "VALID"

    def test_repair_performed_true(self):
        assert self._meta()["repair_performed"] is True

    def test_repair_success_true(self):
        assert self._meta()["repair_success"] is True

    def test_repair_count_one(self):
        assert self._meta()["repair_count"] == 1

    def test_recommended_action_is_repaired(self):
        assert self._meta()["recommended_action"] == "Automatically repaired"

    def test_repair_strategy_present(self):
        assert self._meta().get("repair_strategy") == "BALANCED"

    def test_rescored_true(self):
        assert self._meta()["rescored"] is True

    def test_pipeline_stage_count_8(self):
        assert self._meta()["pipeline_stage_count"] == 8


# ═════════════════════════════════════════════════════════════════════════════
# 4. INVALID after failed repair
# ═════════════════════════════════════════════════════════════════════════════
class TestInvalidAfterFailedRepair:
    def _meta(self):
        kw = _base_kwargs(chunk_id="c1", stage_count=8)
        kw["validation_result"] = _make_val_result(has_issues=True, severity="CRITICAL",
                                                    description="Broken code block",
                                                    rec="Fix the code block")
        kw["revalidation_result"] = _make_val_result(has_issues=True, severity="CRITICAL",
                                                      rec="Fix the code block")
        kw["repair_result"] = _make_repair_result(repair_score=0.3, repaired_chunk_ids=["c1"])
        kw["repaired_chunk_ids"] = {"c1"}
        return build_pipeline_metadata(**kw)

    def test_pipeline_status_invalid(self):
        # Repaired but revalidation still has issues → INVALID
        assert self._meta()["pipeline_status"] == "INVALID"

    def test_repair_performed_true(self):
        assert self._meta()["repair_performed"] is True

    def test_repair_success_false_low_score(self):
        # repair_score=0.3 → below 0.5 threshold
        assert self._meta()["repair_success"] is False

    def test_repair_count_one(self):
        assert self._meta()["repair_count"] == 1


# ═════════════════════════════════════════════════════════════════════════════
# 5. INVALID — issues exist, repair never ran
# ═════════════════════════════════════════════════════════════════════════════
class TestInvalidNoRepair:
    def _meta(self):
        kw = _base_kwargs(chunk_id="c1")
        kw["validation_result"] = _make_val_result(
            has_issues=True, severity="CRITICAL",
            description="Broken table structure", rec="Rebuild table"
        )
        kw["repair_result"] = None
        return build_pipeline_metadata(**kw)

    def test_pipeline_status_invalid(self):
        assert self._meta()["pipeline_status"] == "INVALID"

    def test_validation_status_invalid(self):
        assert self._meta()["validation_status"] == "INVALID"

    def test_repair_performed_false(self):
        assert self._meta()["repair_performed"] is False

    def test_repair_success_false(self):
        assert self._meta()["repair_success"] is False

    def test_repair_count_zero(self):
        assert self._meta()["repair_count"] == 0

    def test_recommended_action_from_validator(self):
        assert self._meta().get("recommended_action") == "Rebuild table"

    def test_no_repair_strategy_key(self):
        assert "repair_strategy" not in self._meta()


# ═════════════════════════════════════════════════════════════════════════════
# 6. SKIPPED — validation unavailable
# ═════════════════════════════════════════════════════════════════════════════
class TestSkippedValidation:
    def _meta(self):
        return build_pipeline_metadata(**_base_kwargs())  # validation_result=None

    def test_validation_status_skipped(self):
        assert self._meta()["validation_status"] == "SKIPPED"

    def test_pipeline_status_skipped(self):
        assert self._meta()["pipeline_status"] == "SKIPPED"

    def test_no_recommended_action(self):
        assert "recommended_action" not in self._meta()

    def test_repair_performed_false(self):
        assert self._meta()["repair_performed"] is False

    def test_repair_success_false(self):
        assert self._meta()["repair_success"] is False


# ═════════════════════════════════════════════════════════════════════════════
# 7. Assertion guard — impossible state must raise
# ═════════════════════════════════════════════════════════════════════════════
class TestImpossibleStateGuard:
    def test_repair_success_true_without_repair_performed_raises(self):
        """Patching repair_result so repair_score>0.5 but chunk NOT in repaired set"""
        kw = _base_kwargs(chunk_id="c1")
        kw["validation_result"] = _make_val_result(has_issues=True)
        kw["repair_result"] = _make_repair_result(repair_score=0.95, repaired_chunk_ids=[])
        # repaired_chunk_ids is empty → repair_performed=False → repair_success must be False
        # → assertion must NOT fire because the builder correctly derives repair_success=False
        meta = build_pipeline_metadata(**kw)
        assert meta["repair_success"] is False
        assert meta["repair_performed"] is False

    def test_repair_performed_false_implies_count_zero(self):
        kw = _base_kwargs(chunk_id="c1")
        kw["repair_result"] = _make_repair_result(repaired_chunk_ids=["other-chunk"])
        meta = build_pipeline_metadata(**kw)
        assert meta["repair_performed"] is False
        assert meta["repair_count"] == 0


# ═════════════════════════════════════════════════════════════════════════════
# 8. recommended_action decision table
# ═════════════════════════════════════════════════════════════════════════════
class TestRecommendedActionDecisionTable:
    def test_valid_no_action(self):
        kw = _base_kwargs()
        kw["validation_result"] = _make_val_result(has_issues=False)
        assert "recommended_action" not in build_pipeline_metadata(**kw)

    def test_skipped_no_action(self):
        assert "recommended_action" not in build_pipeline_metadata(**_base_kwargs())

    def test_repaired_action_is_auto_repaired(self):
        kw = _base_kwargs(chunk_id="c1", stage_count=8)
        kw["validation_result"] = _make_val_result(has_issues=True)
        kw["revalidation_result"] = _make_val_result(has_issues=False)
        kw["repair_result"] = _make_repair_result(repaired_chunk_ids=["c1"])
        kw["repaired_chunk_ids"] = {"c1"}
        assert build_pipeline_metadata(**kw)["recommended_action"] == "Automatically repaired"

    def test_invalid_action_from_validator_rec(self):
        kw = _base_kwargs()
        kw["validation_result"] = _make_val_result(
            has_issues=True, severity="CRITICAL", rec="Refactor this section"
        )
        assert build_pipeline_metadata(**kw)["recommended_action"] == "Refactor this section"

    def test_invalid_no_rec_gives_no_action_key(self):
        kw = _base_kwargs()
        kw["validation_result"] = _make_val_result(has_issues=True)
        # override recommendations to empty
        kw["validation_result"].recommendations = []
        meta = build_pipeline_metadata(**kw)
        assert "recommended_action" not in meta


# ═════════════════════════════════════════════════════════════════════════════
# 9. pipeline_stage_count
# ═════════════════════════════════════════════════════════════════════════════
class TestPipelineStageCount:
    @pytest.mark.parametrize("n", [5, 6, 7, 8])
    def test_count_equals_stage_timings_length(self, n):
        kw = _base_kwargs(stage_count=n)
        assert build_pipeline_metadata(**kw)["pipeline_stage_count"] == n


# ═════════════════════════════════════════════════════════════════════════════
# 10. validation_status always canonical
# ═════════════════════════════════════════════════════════════════════════════
class TestValidationStatusAlwaysCanonical:
    @pytest.mark.parametrize("raw,expected", [
        ("VALID", "VALID"),
        ("INVALID", "INVALID"),
        ("WARNING", "INVALID"),
        ("FAILED", "INVALID"),
        ("CRITICAL", "INVALID"),
    ])
    def test_coercion(self, raw, expected):
        kw = _base_kwargs()
        vr = _make_val_result(has_issues=(raw != "VALID"), overall_status=raw)
        kw["validation_result"] = vr
        meta = build_pipeline_metadata(**kw)
        assert meta["validation_status"] in ("VALID", "INVALID", "SKIPPED"), (
            f"Got unexpected validation_status: {meta['validation_status']}"
        )


# ═════════════════════════════════════════════════════════════════════════════
# 11. pipeline_status always canonical
# ═════════════════════════════════════════════════════════════════════════════
class TestPipelineStatusAlwaysCanonical:
    _ALLOWED = {"VALID", "REPAIRED", "INVALID", "SKIPPED"}

    def _assert_canonical(self, **overrides):
        kw = _base_kwargs()
        kw.update(overrides)
        ps = build_pipeline_metadata(**kw)["pipeline_status"]
        assert ps in self._ALLOWED, f"Invalid pipeline_status: {ps}"

    def test_valid_case(self):
        self._assert_canonical(validation_result=_make_val_result(has_issues=False))

    def test_invalid_case(self):
        self._assert_canonical(validation_result=_make_val_result(has_issues=True))

    def test_skipped_case(self):
        self._assert_canonical()

    def test_repaired_case(self):
        vr = _make_val_result(has_issues=True)
        rv_after = _make_val_result(has_issues=False)
        rr = _make_repair_result(repaired_chunk_ids=["c1"])
        self._assert_canonical(
            validation_result=vr,
            revalidation_result=rv_after,
            repair_result=rr,
            repaired_chunk_ids={"c1"},
        )


# ═════════════════════════════════════════════════════════════════════════════
# 12. End-to-end _build_db_chunks integration
# ═════════════════════════════════════════════════════════════════════════════

def _make_unit():
    u = MagicMock()
    u.semantic_type = "text"
    u.structure_node_id = None
    u.page_start = 1
    u.line_start = 1
    u.line_end = 2
    u.char_start = 0
    u.char_end = 100
    u.content = "This is a test sentence."
    u.metadata = {"content_markdown": u.content}
    return u


def _make_ctx_chunk(chunk_id="c1"):
    c = MagicMock()
    c.id = chunk_id
    c.chunk_index = 0
    c.chunk_hash = "abc"
    c.chunk_signature = "sig"
    c.language = "en"
    c.estimated_tokens = 20
    c.estimated_characters = 100
    c.estimated_words = 15
    c.importance_score = 0.8
    c.retrieval_weight = 1.0
    c.heading_path = ["Section"]
    c.section_path = ["/"]
    c.document_path = "/doc.md"
    c.content = "This is a test sentence."
    c.semantic_units = [_make_unit()]
    c.semantic_boundaries = []
    return c


def _make_pipeline_ctx(chunk_id="c1", val_has_issues=False, repair_executed=False,
                        is_repaired=False, repair_score=0.9, stage_count=7):
    ctx = PipelineContext()
    ctx.pipeline_id = "e2e-test"
    ctx.pipeline_version = "1.0.0"
    ctx.pipeline_health = 0.95
    ctx.fallback_used = False
    ctx.stage_timings = {f"S{i}": 0.01 for i in range(stage_count)}
    ctx.repaired_chunk_ids = {chunk_id} if is_repaired else set()
    ctx.chunks = [_make_ctx_chunk(chunk_id)]
    ctx.scores = []

    ctx.validation_result = _make_val_result(
        has_issues=val_has_issues,
        severity="WARNING",
        rec="Merge with next",
    )
    ctx.revalidation_result = None

    if repair_executed:
        ctx.repair_result = _make_repair_result(
            repair_score=repair_score,
            repaired_chunk_ids=[chunk_id] if is_repaired else [],
        )
        if is_repaired:
            ctx.revalidation_result = _make_val_result(has_issues=False)
    else:
        ctx.repair_result = None

    return ctx


class TestBuildDbChunksEndToEnd:
    def test_valid_no_repair_produces_consistent_metadata(self):
        ctx = _make_pipeline_ctx(val_has_issues=False, repair_executed=False)
        meta = _build_db_chunks(ctx)[0]["metadata_json"]
        assert meta["validation_status"] == "VALID"
        assert meta["pipeline_status"] == "VALID"
        assert meta["repair_performed"] is False
        assert meta["repair_success"] is False
        assert meta["repair_count"] == 0
        assert "recommended_action" not in meta

    def test_repaired_produces_consistent_metadata(self):
        ctx = _make_pipeline_ctx(val_has_issues=True, repair_executed=True,
                                  is_repaired=True, repair_score=0.9, stage_count=8)
        meta = _build_db_chunks(ctx)[0]["metadata_json"]
        assert meta["pipeline_status"] == "REPAIRED"
        assert meta["repair_performed"] is True
        assert meta["repair_success"] is True
        assert meta["recommended_action"] == "Automatically repaired"
        assert meta["pipeline_stage_count"] == 8

    def test_invalid_no_repair_has_recommendation(self):
        ctx = _make_pipeline_ctx(val_has_issues=True, repair_executed=False)
        meta = _build_db_chunks(ctx)[0]["metadata_json"]
        assert meta["pipeline_status"] == "INVALID"
        assert meta["repair_performed"] is False
        assert meta.get("recommended_action") == "Merge with next"

    def test_skipped_validation_produces_skipped_status(self):
        ctx = _make_pipeline_ctx()
        ctx.validation_result = None
        ctx.repair_result = None
        meta = _build_db_chunks(ctx)[0]["metadata_json"]
        assert meta["validation_status"] == "SKIPPED"
        assert meta["pipeline_status"] == "SKIPPED"
        assert "recommended_action" not in meta
