import time
import uuid
import hashlib
from typing import List, Optional, Tuple, Dict, Any

from app.services.semantic.base_boundary_predictor import BaseBoundaryPredictor
from app.services.semantic.semantic_unit import SemanticUnit
from app.services.semantic.semantic_boundary import SemanticBoundary, BoundaryTrace
from app.services.semantic.semantic_distance import calculate_semantic_distance
from app.services.semantic.boundary_type_registry import BoundaryTypeRegistry
from app.services.semantic.semantic_config import SemanticConfiguration
from app.services.semantic.semantic_pipeline_context import SemanticPipelineContext
from app.services.semantic.semantic_boundary_rules import (
    HeadingBoundaryRule,
    SectionBoundaryRule,
    CodeBoundaryRule,
    TableBoundaryRule,
    FormulaBoundaryRule,
    WarningBoundaryRule,
    QuestionAnswerBoundaryRule,
    TopicShiftBoundaryRule,
    FallbackBoundaryRule
)

class RuleBoundaryPredictor(BaseBoundaryPredictor):
    def __init__(
        self,
        registry: Optional[BoundaryTypeRegistry] = None,
        config: Optional[SemanticConfiguration] = None
    ):
        self.registry = registry or BoundaryTypeRegistry()
        self.config = config or SemanticConfiguration()
        self.rules = [
            HeadingBoundaryRule(),
            SectionBoundaryRule(),
            CodeBoundaryRule(),
            TableBoundaryRule(),
            FormulaBoundaryRule(),
            WarningBoundaryRule(),
            QuestionAnswerBoundaryRule(),
            TopicShiftBoundaryRule(),
            FallbackBoundaryRule()
        ]

    def predict_boundaries(
        self,
        units: List[SemanticUnit],
        context: Optional[SemanticPipelineContext] = None
    ) -> List[SemanticBoundary]:
        boundaries: List[SemanticBoundary] = []
        if not units:
            return boundaries

        # 1. Evaluate transitions
        for i in range(len(units) - 1):
            unit_a = units[i]
            unit_b = units[i + 1]
            boundary = self._predict_transition(unit_a, unit_b, context)
            boundaries.append(boundary)

        # 2. Document End Boundary
        last_unit = units[-1]
        doc_end_id = uuid.uuid4()
        
        # Deterministic fingerprint & hash for Document End
        fp_payload = f"None-{last_unit.id}-DOCUMENT_END-{last_unit.char_end}"
        fingerprint = hashlib.sha256(fp_payload.encode("utf-8")).hexdigest()

        doc_end_boundary = SemanticBoundary(
            id=doc_end_id,
            previous_unit_id=last_unit.id,
            next_unit_id=None,
            page=last_unit.page_end,
            line=last_unit.line_end,
            char_offset=last_unit.char_end,
            boundary_type="DOCUMENT_END",
            base_confidence=1.0,
            final_confidence=1.0,
            priority=100,
            reason="Reached end of document structure",
            matched_rules=["document_end"],
            generated_from_rules=["document_end"],
            generated_from_nodes=[str(last_unit.structure_node_id)],
            boundary_hash=fingerprint,
            boundary_signature=f"sig_{fingerprint[:16]}",
            boundary_version="1.0",
            quality_score=1.0,
            quality_breakdown={"base": 1.0},
            chunk_recommendation="preserve"
        )
        boundaries.append(doc_end_boundary)

        return boundaries

    def _predict_transition(
        self,
        unit_a: SemanticUnit,
        unit_b: SemanticUnit,
        context: Optional[SemanticPipelineContext]
    ) -> SemanticBoundary:
        matched_rules = []
        rejected_rules = []
        detected_rule = None
        b_type = "FALLBACK_BOUNDARY"

        # 1. Rules Matching
        for rule in self.rules:
            res = rule.detect(unit_a, unit_b)
            if res:
                if not detected_rule:
                    detected_rule = res
                    b_type = res["boundary_type"]
                    matched_rules.append(res["rule_name"])
                else:
                    rejected_rules.append(res["rule_name"])
            else:
                # Store the rule name as rejected if it didn't trigger
                # We instantiate and fetch rule class name or construct rule name mapping
                rule_name = rule.__class__.__name__.replace("BoundaryRule", "").lower()
                rejected_rules.append(rule_name)

        if not self.registry.exists(b_type):
            b_type = "FALLBACK_BOUNDARY"

        # 2. Extract values
        base_confidence = detected_rule.get("base_confidence", 0.20) if detected_rule else 0.20
        heading_bonus = detected_rule.get("heading_bonus", 0.0) if detected_rule else 0.0
        metadata_bonus = detected_rule.get("metadata_bonus", 0.0) if detected_rule else 0.0
        neighbor_bonus = detected_rule.get("neighbor_bonus", 0.0) if detected_rule else 0.0
        semantic_bonus = detected_rule.get("semantic_bonus", 0.0) if detected_rule else 0.0
        structure_bonus = detected_rule.get("structure_bonus", 0.0) if detected_rule else 0.0
        priority = detected_rule.get("priority", 20) if detected_rule else 20
        reason = detected_rule.get("reason", "Fallback block transition") if detected_rule else "Fallback block transition"

        # Extra checks: Page changes
        if unit_a.page_end != unit_b.page_start:
            metadata_bonus += 0.15
            matched_rules.append("page_change")

        # 3. Semantic distance & similarity bonus
        distance, similarity = calculate_semantic_distance(unit_a, unit_b)
        similarity_bonus = similarity * 0.10
        
        # Noise penalty (penalize if unit is extremely short)
        noise_penalty = 0.0
        if len(unit_a.content.split()) < 3 or len(unit_b.content.split()) < 3:
            noise_penalty = 0.15

        # 4. Adaptive Confidence
        type_weight = self.registry.priority(b_type) / 100.0 * 0.10
        final_confidence = base_confidence + heading_bonus + metadata_bonus + neighbor_bonus + semantic_bonus + structure_bonus + similarity_bonus + type_weight - noise_penalty
        final_confidence = round(min(1.0, max(0.0, final_confidence)), 2)

        # 5. Boundary Context
        previous_heading = unit_a.heading_path[-1] if unit_a.heading_path else None
        current_heading = unit_b.heading_path[-1] if unit_b.heading_path else None
        next_heading = None # Can be filled if next unit exists, but current unit heading is sufficient

        # 6. Importance Score & Retrieval Hints & Recommendation
        # Table, code, warnings increase boundary importance
        importance_score = max(unit_a.importance_score, unit_b.importance_score)
        if b_type in ("CODE_START", "CODE_END", "TABLE_START", "TABLE_END"):
            importance_score = min(1.0, importance_score + 0.15)
            
        retrieval_weight = round(importance_score * 1.2, 2)
        merge_priority = 100 - int(importance_score * 100)

        contains_code = (unit_a.semantic_type == "code" or unit_b.semantic_type == "code")
        contains_warning = (unit_a.semantic_type == "warning" or unit_b.semantic_type == "warning")
        contains_table = (unit_a.semantic_type == "table" or unit_b.semantic_type == "table")
        contains_formula = (unit_a.semantic_type == "formula" or unit_b.semantic_type == "formula")
        contains_definition = (unit_a.semantic_type == "definition" or unit_b.semantic_type == "definition")

        retrieval_hints = {
            "contains_code": contains_code,
            "contains_warning": contains_warning,
            "contains_table": contains_table,
            "contains_formula": contains_formula,
            "contains_definition": contains_definition,
            "recommended_expansion": "previous_heading" if previous_heading else "none",
            "recommended_merge": (similarity > 0.80 and not contains_code)
        }

        # Chunk Recommendation
        if b_type in ("HEADING_BREAK", "SECTION_BREAK", "CODE_START", "CODE_END", "TABLE_START", "TABLE_END"):
            chunk_recommendation = "split"
        elif similarity > 0.75:
            chunk_recommendation = "merge"
        else:
            chunk_recommendation = "preserve"

        # 7. Quality Score & Quality Breakdown
        # quality_score = confidence * 0.3 + importance * 0.3 + semantic_distance * 0.2 + metadata_richness * 0.2
        metadata_richness = len(unit_b.metadata_snapshot.keys()) / 10.0 if hasattr(unit_b, "metadata_snapshot") else 0.2
        quality_score = final_confidence * 0.3 + importance_score * 0.3 + distance * 0.2 + min(0.2, metadata_richness)
        quality_score = round(min(1.0, max(0.0, quality_score)), 2)

        quality_breakdown = {
            "confidence_contribution": round(final_confidence * 0.3, 2),
            "importance_contribution": round(importance_score * 0.3, 2),
            "distance_contribution": round(distance * 0.2, 2),
            "metadata_contribution": round(min(0.2, metadata_richness), 2)
        }

        # 8. Deterministic Fingerprint, Hash and Signature
        fp_payload = f"{unit_a.id}-{unit_b.id}-{b_type}-{unit_a.char_end}"
        boundary_hash = hashlib.sha256(fp_payload.encode("utf-8")).hexdigest()
        boundary_signature = f"sig_{boundary_hash[:16]}"

        boundary_id = uuid.uuid4()
        boundary = SemanticBoundary(
            id=boundary_id,
            previous_unit_id=unit_a.id,
            next_unit_id=unit_b.id,
            page=unit_a.page_end,
            line=unit_a.line_end,
            char_offset=unit_a.char_end,
            boundary_type=b_type,
            base_confidence=base_confidence,
            heading_bonus=heading_bonus,
            metadata_bonus=metadata_bonus,
            neighbor_bonus=neighbor_bonus,
            semantic_bonus=semantic_bonus,
            structure_bonus=structure_bonus,
            final_confidence=final_confidence,
            priority=priority,
            reason=reason,
            score_breakdown={
                "base_confidence": base_confidence,
                "heading_bonus": heading_bonus,
                "metadata_bonus": metadata_bonus,
                "neighbor_bonus": neighbor_bonus,
                "semantic_bonus": semantic_bonus,
                "structure_bonus": structure_bonus,
                "similarity_bonus": round(similarity_bonus, 2),
                "type_weight": round(type_weight, 2),
                "noise_penalty": noise_penalty
            },
            metadata={
                "heading_path": unit_b.heading_path,
                "section_path": unit_b.section_path,
                "language": unit_b.language,
                "semantic_type_before": unit_a.semantic_type,
                "semantic_type_after": unit_b.semantic_type
            },
            matched_rules=matched_rules,
            rejected_rules=rejected_rules,
            confidence_breakdown={
                "base": base_confidence,
                "heading_bonus": heading_bonus,
                "metadata_bonus": metadata_bonus,
                "similarity_bonus": similarity_bonus,
                "noise_penalty": noise_penalty
            },
            distance_breakdown={
                "distance": distance,
                "similarity": similarity
            },
            final_reason=f"Transition from {unit_a.semantic_type} to {unit_b.semantic_type} triggered {matched_rules[0]}",
            importance_score=importance_score,
            retrieval_weight=retrieval_weight,
            merge_priority=merge_priority,
            retrieval_hints=retrieval_hints,
            chunk_recommendation=chunk_recommendation,
            previous_heading=previous_heading,
            current_heading=current_heading,
            section_path=unit_b.section_path,
            heading_path=unit_b.heading_path,
            document_path=unit_b.document_path,
            language=unit_b.language,
            metadata_snapshot=unit_b.metadata if hasattr(unit_b, "metadata") else {},
            boundary_hash=boundary_hash,
            boundary_signature=boundary_signature,
            boundary_version="1.0",
            generated_from_rules=matched_rules,
            generated_from_nodes=[str(unit_a.structure_node_id), str(unit_b.structure_node_id)],
            generated_from_metadata=unit_b.metadata if hasattr(unit_b, "metadata") else {},
            quality_score=quality_score,
            quality_breakdown=quality_breakdown
        )

        return boundary
