"""
Concrete Pipeline Stages — Phase 10.6

Each stage wraps exactly one logical step in the Semantic Pipeline.
Stages mutate PipelineContext and return a StageResult.
"""
from __future__ import annotations
import time
import logging
from typing import List, Any

from app.services.pipeline.pipeline_stage import PipelineStage
from app.services.pipeline.pipeline_context import PipelineContext
from app.services.pipeline.pipeline_stage_result import StageResult

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Stage 1: Structure Analysis
# ─────────────────────────────────────────────────────────────────────────────
class StructureAnalysisStage(PipelineStage):
    def name(self) -> str:
        return "StructureAnalysisStage"

    def dependencies(self) -> List[str]:
        return []

    def execute(self, ctx: PipelineContext) -> StageResult:
        t0 = time.time()
        result = StageResult(stage_name=self.name(), stage_version=self.version())
        try:
            # nodes already on ctx from document structure analysis in processing_service
            result.add_output("node_count", len(ctx.nodes))
            result.statistics["node_count"] = len(ctx.nodes)
        except Exception as exc:
            result.add_error(str(exc))
        result.execution_time = time.time() - t0
        return result


# ─────────────────────────────────────────────────────────────────────────────
# Stage 2: Semantic Unit Detection
# ─────────────────────────────────────────────────────────────────────────────
class SemanticUnitStage(PipelineStage):
    def name(self) -> str:
        return "SemanticUnitStage"

    def dependencies(self) -> List[str]:
        return ["StructureAnalysisStage"]

    def execute(self, ctx: PipelineContext) -> StageResult:
        t0 = time.time()
        result = StageResult(stage_name=self.name(), stage_version=self.version())
        try:
            from app.services.semantic.semantic_pipeline_context import SemanticPipelineContext
            from app.services.semantic.semantic_unit_detector import SemanticUnitDetector
            sem_context = SemanticPipelineContext()
            if ctx.document_version:
                sem_context.document_version_id = ctx.document_version.id
            detector = SemanticUnitDetector(context=sem_context)
            ctx.semantic_units = detector.detect_semantic_units(ctx.nodes)
            result.add_output("unit_count", len(ctx.semantic_units))
            result.statistics["unit_count"] = len(ctx.semantic_units)
        except Exception as exc:
            result.add_error(str(exc))
        result.execution_time = time.time() - t0
        return result


# ─────────────────────────────────────────────────────────────────────────────
# Stage 3: Boundary Detection
# ─────────────────────────────────────────────────────────────────────────────
class BoundaryDetectionStage(PipelineStage):
    def name(self) -> str:
        return "BoundaryDetectionStage"

    def dependencies(self) -> List[str]:
        return ["SemanticUnitStage"]

    def execute(self, ctx: PipelineContext) -> StageResult:
        t0 = time.time()
        result = StageResult(stage_name=self.name(), stage_version=self.version())
        try:
            from app.services.semantic.semantic_pipeline_context import SemanticPipelineContext
            from app.services.semantic.semantic_boundary_detector import SemanticBoundaryDetector
            sem_context = SemanticPipelineContext()
            if ctx.document_version:
                sem_context.document_version_id = ctx.document_version.id
            detector = SemanticBoundaryDetector(context=sem_context)
            ctx.boundaries = detector.detect_boundaries(ctx.semantic_units)
            result.add_output("boundary_count", len(ctx.boundaries))
            result.statistics["boundary_count"] = len(ctx.boundaries)
        except Exception as exc:
            result.add_error(str(exc))
        result.execution_time = time.time() - t0
        return result


# ─────────────────────────────────────────────────────────────────────────────
# Stage 4: Semantic Chunk Builder
# ─────────────────────────────────────────────────────────────────────────────
class SemanticChunkBuilderStage(PipelineStage):
    def name(self) -> str:
        return "SemanticChunkBuilderStage"

    def dependencies(self) -> List[str]:
        return ["BoundaryDetectionStage"]

    def execute(self, ctx: PipelineContext) -> StageResult:
        t0 = time.time()
        result = StageResult(stage_name=self.name(), stage_version=self.version())
        try:
            from app.services.chunking.semantic_chunk_builder import SemanticChunkBuilder
            builder = SemanticChunkBuilder()
            ctx.chunks = builder.build_chunks(ctx.semantic_units, ctx.boundaries)
            result.add_output("chunk_count", len(ctx.chunks))
            result.statistics["chunk_count"] = len(ctx.chunks)
        except Exception as exc:
            result.add_error(str(exc))
        result.execution_time = time.time() - t0
        return result


# ─────────────────────────────────────────────────────────────────────────────
# Stage 5: Chunk Scoring
# ─────────────────────────────────────────────────────────────────────────────
class ChunkScoringStage(PipelineStage):
    def name(self) -> str:
        return "ChunkScoringStage"

    def dependencies(self) -> List[str]:
        return ["SemanticChunkBuilderStage"]

    def execute(self, ctx: PipelineContext) -> StageResult:
        t0 = time.time()
        result = StageResult(stage_name=self.name(), stage_version=self.version())
        try:
            from app.services.scoring.scoring_profile import ScoringProfile
            from app.services.scoring.chunk_scoring_engine import ChunkScoringEngine
            from app.services.scoring.scoring_validator import ScoringValidator
            profile = ScoringProfile()
            ctx.scores = ChunkScoringEngine.score_chunks(ctx.chunks, profile)
            val = ScoringValidator.validate_pipeline(ctx.scores)
            if not val.is_valid:
                result.add_warning(f"Scoring validation: {val.summary()}")
            result.add_output("score_count", len(ctx.scores))
            result.statistics["score_count"] = len(ctx.scores)
            result.statistics["scoring_version"] = profile.scoring_version
        except Exception as exc:
            result.add_error(str(exc))
            ctx.scores = []
        result.execution_time = time.time() - t0
        return result


# ─────────────────────────────────────────────────────────────────────────────
# Stage 6: Semantic Validation
# ─────────────────────────────────────────────────────────────────────────────
class SemanticValidationStage(PipelineStage):
    def name(self) -> str:
        return "SemanticValidationStage"

    def dependencies(self) -> List[str]:
        return ["ChunkScoringStage"]

    def execute(self, ctx: PipelineContext) -> StageResult:
        t0 = time.time()
        result = StageResult(stage_name=self.name(), stage_version=self.version())
        try:
            from app.services.validation.semantic_validation_profile import SemanticValidationProfile
            from app.services.validation.semantic_validator import SemanticValidator
            profile = SemanticValidationProfile()
            ctx.validation_result = SemanticValidator.validate_pipeline(ctx.chunks, profile)
            vr = ctx.validation_result
            result.add_output("validation_status", vr.overall_status)
            result.add_output("issue_count", len(vr.issues))
            result.statistics["validation_score"] = vr.overall_validation_score
            result.statistics["critical_issues"] = vr.critical_count
            result.statistics["warning_issues"] = vr.warning_count
        except Exception as exc:
            result.add_error(str(exc))
            ctx.validation_result = None
        result.execution_time = time.time() - t0
        return result


# ─────────────────────────────────────────────────────────────────────────────
# Stage 7: Semantic Repair
# ─────────────────────────────────────────────────────────────────────────────
class SemanticRepairStage(PipelineStage):
    def name(self) -> str:
        return "SemanticRepairStage"

    def dependencies(self) -> List[str]:
        return ["SemanticValidationStage"]

    def supports(self, ctx: PipelineContext) -> bool:
        # Only run if validation found issues
        return bool(ctx.validation_result and ctx.validation_result.issues)

    def execute(self, ctx: PipelineContext) -> StageResult:
        t0 = time.time()
        result = StageResult(stage_name=self.name(), stage_version=self.version())
        try:
            from app.services.validation.semantic_repair_engine import SemanticRepairEngine
            from app.services.validation.repair_strategy import BalancedRepairStrategy
            from app.services.validation.semantic_validation_profile import SemanticValidationProfile
            from app.services.validation.semantic_validator import SemanticValidator

            engine = SemanticRepairEngine(strategy=BalancedRepairStrategy())
            ctx.repair_result = engine.repair_pipeline(ctx.chunks, ctx.validation_result)
            ctx.repaired_chunk_ids = {str(r.affected_chunk) for r in ctx.repair_result.repaired_issues}

            # Re-validate after repair
            profile = SemanticValidationProfile()
            ctx.revalidation_result = SemanticValidator.validate_pipeline(ctx.chunks, profile)

            # Re-score changed chunks only
            if ctx.repaired_chunk_ids:
                from app.services.scoring.scoring_profile import ScoringProfile
                from app.services.scoring.chunk_scoring_engine import ChunkScoringEngine
                sp = ScoringProfile()
                changed = [c for c in ctx.chunks if str(c.id) in ctx.repaired_chunk_ids]
                rescored = ChunkScoringEngine.score_chunks(changed, sp)
                for ns in rescored:
                    for i, old in enumerate(ctx.scores):
                        if old.score_signature == ns.score_signature:
                            ctx.scores[i] = ns
                            break
                    else:
                        ctx.scores.append(ns)

            result.add_output("repaired_count", len(ctx.repair_result.repaired_issues))
            result.add_output("failed_repairs", len(ctx.repair_result.failed_repairs))
            result.statistics["repair_score"] = ctx.repair_result.repair_score
        except Exception as exc:
            result.add_error(str(exc))
            ctx.repair_result = None
        result.execution_time = time.time() - t0
        return result


# ─────────────────────────────────────────────────────────────────────────────
# Stage 8: Store Chunks (ORM mapping only — no DB calls here)
# ─────────────────────────────────────────────────────────────────────────────
class StoreChunkStage(PipelineStage):
    def name(self) -> str:
        return "StoreChunkStage"

    def dependencies(self) -> List[str]:
        return ["SemanticRepairStage"]

    def execute(self, ctx: PipelineContext) -> StageResult:
        t0 = time.time()
        result = StageResult(stage_name=self.name(), stage_version=self.version())
        try:
            ctx.db_chunks = _build_db_chunks(ctx)
            result.add_output("db_chunk_count", len(ctx.db_chunks))
            result.statistics["db_chunk_count"] = len(ctx.db_chunks)
        except Exception as exc:
            result.add_error(str(exc))
        result.execution_time = time.time() - t0
        return result


# ─────────────────────────────────────────────────────────────────────────────
# Shared helper — ORM dictionary builder
# ─────────────────────────────────────────────────────────────────────────────
def _build_db_chunks(ctx: PipelineContext):
    """Convert SemanticChunks + scores into ORM-ready dicts."""
    from app.services.metadata_builder import build_metadata
    from app.services.scoring.scoring_profile import ScoringProfile

    profile = ScoringProfile()
    val_result = ctx.validation_result
    repair_result = ctx.repair_result
    revalidation_result = ctx.revalidation_result
    val_profile_version = "1.0"
    try:
        from app.services.validation.semantic_validation_profile import SemanticValidationProfile
        val_profile_version = SemanticValidationProfile().validation_version
    except Exception:
        pass

    chunks = []
    for idx, c in enumerate(ctx.chunks):
        main_node_id = c.semantic_units[0].structure_node_id if c.semantic_units else None
        heading = c.heading_path[-1] if c.heading_path else ""
        is_code = any(u.semantic_type == "code" for u in c.semantic_units)
        lang = c.language

        c_meta = build_metadata(c.content, is_code, lang if is_code else None)
        if not isinstance(c_meta, dict):
            c_meta = {}

        # Scores
        if idx < len(ctx.scores):
            s = ctx.scores[idx]
            c_meta.update({
                "overall_score": s.overall_score,
                "quality_score": s.quality_score,
                "ranking_score": s.ranking_score,
                "retrieval_priority": s.retrieval_priority,
                "context_priority": s.context_priority,
                "ranking_priority": s.ranking_priority,
                "recommendation": s.recommendation,
                "retrieval_modes": [s.recommended_retrieval_mode],
                "recommended_retrieval_mode": s.recommended_retrieval_mode,
                "quality_breakdown": s.quality_breakdown,
                "score_breakdown": s.score_breakdown,
                "penalties": s.penalties,
                "bonuses": s.bonuses,
                "confidence": s.confidence,
                "score_signature": s.score_signature,
                "score_hash": s.score_hash,
                "scoring_version": s.score_version,
                "scoring_trace": s.scoring_trace,
                "matched_features": s.matched_features,
            })
        else:
            c_meta.update({
                "overall_score": 0.5,
                "quality_score": 0.5,
                "ranking_score": 0.5,
                "retrieval_priority": 0.5,
                "context_priority": 0.5,
                "ranking_priority": 0.5,
                "recommendation": "GOOD_FOR_RETRIEVAL",
                "retrieval_modes": ["SEMANTIC"],
                "recommended_retrieval_mode": "SEMANTIC",
                "quality_breakdown": {},
                "score_breakdown": {},
                "penalties": [],
                "bonuses": [],
                "confidence": 0.8,
                "score_signature": c.chunk_signature,
                "score_hash": "",
                "scoring_version": profile.scoring_version,
                "scoring_trace": {},
                "matched_features": [],
            })

        # ── Validation + Repair + Pipeline metadata ───────────────────────────
        from app.services.pipeline.pipeline_metadata_builder import build_pipeline_metadata
        c_meta.update(build_pipeline_metadata(
            chunk_id=str(c.id),
            validation_result=val_result,
            repair_result=repair_result,
            revalidation_result=revalidation_result,
            repaired_chunk_ids=ctx.repaired_chunk_ids,
            stage_timings=ctx.stage_timings,
            pipeline_id=ctx.pipeline_id,
            pipeline_version=ctx.pipeline_version,
            pipeline_health=ctx.pipeline_health,
            fallback_used=ctx.fallback_used,
            val_profile_version=val_profile_version,
        ))

        c_meta.update({
            "heading_path": c.heading_path,
            "section_path": c.section_path,
            "document_path": c.document_path,
            "semantic_types": list(set(u.semantic_type for u in c.semantic_units)),
            "boundary_types": list(set(b.boundary_type for b in c.semantic_boundaries)),
            "contains_code": is_code,
            "contains_table": any(u.semantic_type == "table" for u in c.semantic_units),
            "contains_formula": any(u.semantic_type == "formula" for u in c.semantic_units),
            "contains_list": any(u.semantic_type == "list" for u in c.semantic_units),
            "language": c.language,
            "estimated_tokens": c.estimated_tokens,
            "importance_score": c.importance_score,
            "retrieval_weight": c.retrieval_weight,
        })

        content_markdown = " ".join([u.metadata.get("content_markdown", u.content) for u in c.semantic_units])
        page_start = c.semantic_units[0].page_start if c.semantic_units else 1
        line_start = c.semantic_units[0].line_start if c.semantic_units else 1
        line_end = c.semantic_units[-1].line_end if c.semantic_units else 1
        char_start = c.semantic_units[0].char_start if c.semantic_units else 0
        char_end = c.semantic_units[-1].char_end if c.semantic_units else 0

        chunks.append({
            "structure_node_id": main_node_id,
            "chunk_index": c.chunk_index,
            "content": c.content,
            "content_markdown": content_markdown,
            "page_number": page_start,
            "line_start": line_start,
            "line_end": line_end,
            "char_start": char_start,
            "char_end": char_end,
            "token_count": c.estimated_tokens,
            "char_count": c.estimated_characters,
            "word_count": c.estimated_words,
            "hash": c.chunk_hash,
            "heading": heading,
            "metadata_json": c_meta,
        })
    return chunks
