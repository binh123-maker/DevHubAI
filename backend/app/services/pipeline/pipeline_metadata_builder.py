"""
Pipeline Metadata Builder — Phase 10.6A

Single source of truth for all metadata written to DocumentChunk.metadata_json.

Rules enforced:
  - validation_status: VALID | INVALID | SKIPPED  (no WARNING/FAILED)
  - pipeline_status:   VALID | REPAIRED | INVALID | SKIPPED
  - recommended_action: only from validator.recommendations, never from issue descriptions
  - repair_* fields: derived ONLY from the actual SemanticRepairResult object
  - repair_success cannot be True when repair_performed is False (assertion guard)
  - repair_count counts only issues repaired for THIS specific chunk
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Set

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Allowed value sets                                                            #
# --------------------------------------------------------------------------- #
_VALID_VALIDATION_STATUSES = frozenset({"VALID", "INVALID", "SKIPPED"})
_VALID_PIPELINE_STATUSES = frozenset({"VALID", "REPAIRED", "INVALID", "SKIPPED"})


def _coerce_validation_status(raw: str) -> str:
    """Map any legacy/internal status to the canonical three values."""
    if raw in _VALID_VALIDATION_STATUSES:
        return raw
    # WARNING / FAILED → INVALID (they only occur when there are issues)
    return "INVALID"


def build_pipeline_metadata(
    *,
    chunk_id: str,
    validation_result: Optional[Any],
    repair_result: Optional[Any],
    revalidation_result: Optional[Any],
    repaired_chunk_ids: Set[str],
    stage_timings: Dict[str, float],
    pipeline_id: str,
    pipeline_version: str,
    pipeline_health: float,
    fallback_used: bool,
    val_profile_version: str = "1.0",
) -> Dict[str, Any]:
    """
    Build the complete validation / repair / pipeline portion of metadata_json.

    Args:
        chunk_id:            str(c.id) for the chunk being processed
        validation_result:   SemanticValidationResult (or None if skipped)
        repair_result:       SemanticRepairResult (or None if repair never ran)
        revalidation_result: SemanticValidationResult after repair (or None)
        repaired_chunk_ids:  set of chunk IDs that were individually repaired
        stage_timings:       ctx.stage_timings (used for pipeline_stage_count)
        pipeline_id:         ctx.pipeline_id
        pipeline_version:    ctx.pipeline_version
        pipeline_health:     ctx.pipeline_health float
        fallback_used:       ctx.fallback_used bool
        val_profile_version: validation profile version string

    Returns:
        dict ready to be merged into c_meta via c_meta.update(...)
    """
    is_repaired = chunk_id in repaired_chunk_ids

    # ── Determine which validation result to read for this chunk ─────────────
    # Repaired chunks should show their post-repair validation state
    effective_val = (
        revalidation_result
        if (is_repaired and revalidation_result is not None)
        else validation_result
    )

    # ── Validation fields ─────────────────────────────────────────────────────
    if effective_val is None:
        val_status = "SKIPPED"
        val_health = 1.0
        val_score = 1.0
        has_issues = False
        validator_recommendations: list = []
    else:
        raw_status = getattr(effective_val, "overall_status", "VALID")
        has_issues = bool(getattr(effective_val, "issues", []))
        # Normalise: only VALID / INVALID allowed (validator already sets these
        # via __post_init__; guard in case older code passes WARNING/FAILED)
        val_status = _coerce_validation_status(raw_status) if has_issues else "VALID"
        val_health = float(getattr(effective_val, "overall_validation_score", 1.0))
        val_score = val_health
        validator_recommendations = list(getattr(effective_val, "recommendations", []) or [])

    # ── Repair fields — derived exclusively from repair_result ───────────────
    repair_executed = repair_result is not None
    repair_performed = repair_executed and is_repaired

    if repair_performed:
        # Count only repaired issues that belong to THIS chunk
        all_repaired = getattr(repair_result, "repaired_issues", []) or []
        chunk_repair_count = sum(
            1 for r in all_repaired
            if str(getattr(r, "affected_chunk", "")) == chunk_id
        )
        # repair_success: engine score > 0.5 AND at least one issue was repaired for this chunk
        repair_success = (
            getattr(repair_result, "repair_score", 0.0) > 0.5
            and chunk_repair_count > 0
        )
        repair_confidence = float(getattr(repair_result, "repair_confidence", 0.0))
    else:
        chunk_repair_count = 0
        repair_success = False
        repair_confidence = 0.0

    # ── Assertion guard — impossible state check ──────────────────────────────
    assert not (repair_success and not repair_performed), (
        f"IMPOSSIBLE STATE: repair_success=True but repair_performed=False "
        f"for chunk {chunk_id}"
    )

    # ── pipeline_status decision table ────────────────────────────────────────
    if effective_val is None:
        pipeline_status = "SKIPPED"
    elif is_repaired:
        # Use post-repair validation to decide success
        post_val = revalidation_result if revalidation_result is not None else effective_val
        post_has_issues = bool(getattr(post_val, "issues", []))
        pipeline_status = "REPAIRED" if not post_has_issues else "INVALID"
    elif not has_issues:
        pipeline_status = "VALID"
    else:
        pipeline_status = "INVALID"

    # ── recommended_action decision table ─────────────────────────────────────
    # Only populate when there is actually something to recommend
    if pipeline_status in ("VALID", "SKIPPED"):
        recommended_action = None
    elif pipeline_status == "REPAIRED":
        recommended_action = "Automatically repaired"
    else:
        # INVALID — first non-empty recommendation from validator
        recommended_action = next(
            (r for r in validator_recommendations if r),
            None,
        )

    # ── Final post-repair health ──────────────────────────────────────────────
    final_val = revalidation_result if revalidation_result is not None else effective_val
    overall_health = float(getattr(final_val, "overall_validation_score", 1.0)) if final_val else 1.0

    # ── Assemble output dict ──────────────────────────────────────────────────
    meta: Dict[str, Any] = {
        # Validation
        "validation_status": val_status,
        "validation_health": val_health,
        "validation_score": val_score,
        "validation_version": val_profile_version,
        # Repair — always present so consumers don't need key-existence checks
        "repair_performed": repair_performed,
        "repair_success": repair_success,
        "repair_count": chunk_repair_count,
        "repair_confidence": repair_confidence,
        # Shared post-repair
        "rescored": is_repaired,
        "overall_health": overall_health,
        "pipeline_status": pipeline_status,
        # Pipeline provenance
        "pipeline_version": pipeline_version,
        "pipeline_id": pipeline_id,
        "pipeline_health": pipeline_health,
        "pipeline_stage_count": len(stage_timings),
        "fallback_used": fallback_used,
        "stage_timings": stage_timings,
        "semantic_pipeline": True,
    }

    # Only write repair operational fields when repair actually executed
    if repair_executed:
        meta["repair_strategy"] = "BALANCED"
        meta["repair_version"] = getattr(repair_result, "repair_version", "1.0")

    # Only write recommended_action when it has meaningful content
    if recommended_action:
        meta["recommended_action"] = recommended_action

    return meta
