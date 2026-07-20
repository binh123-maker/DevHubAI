import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class BoundaryTrace:
    matched_rules: List[str] = field(default_factory=list)
    boundary_type: str = "TOPIC_SHIFT"
    confidence_breakdown: Dict[str, float] = field(default_factory=dict)
    neighbor_analysis: Dict[str, Any] = field(default_factory=dict)
    metadata_used: Dict[str, Any] = field(default_factory=dict)
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "matched_rules": self.matched_rules,
            "boundary_type": self.boundary_type,
            "confidence_breakdown": self.confidence_breakdown,
            "neighbor_analysis": self.neighbor_analysis,
            "metadata_used": self.metadata_used,
            "reason": self.reason
        }

    def pretty_print(self) -> str:
        breakdown_str = ", ".join([f"{k}: {v:.2f}" for k, v in self.confidence_breakdown.items()])
        return (
            f"=== Boundary Trace ===\n"
            f"Type: {self.boundary_type}\n"
            f"Matched Rules: {self.matched_rules}\n"
            f"Confidence Breakdown: {breakdown_str}\n"
            f"Neighbor Analysis: {self.neighbor_analysis}\n"
            f"Reason: {self.reason}"
        )

@dataclass
class SemanticBoundary:
    id: uuid.UUID
    previous_unit_id: Optional[uuid.UUID]
    next_unit_id: Optional[uuid.UUID]
    page: Optional[int]
    line: Optional[int]
    char_offset: Optional[int]
    boundary_type: str
    
    base_confidence: float = 0.40
    heading_bonus: float = 0.0
    metadata_bonus: float = 0.0
    neighbor_bonus: float = 0.0
    semantic_bonus: float = 0.0
    structure_bonus: float = 0.0
    final_confidence: float = 0.40
    
    priority: int = 50
    reason: str = ""
    score_breakdown: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # 10.2B / 10.2C Explainability, Context, Retrieval hints, Chunk Recommendation
    matched_rules: List[str] = field(default_factory=list)
    rejected_rules: List[str] = field(default_factory=list)
    confidence_breakdown: Dict[str, float] = field(default_factory=dict)
    distance_breakdown: Dict[str, float] = field(default_factory=dict)
    final_reason: str = ""
    
    importance_score: float = 0.50
    retrieval_weight: float = 1.0
    merge_priority: int = 50
    retrieval_hints: Dict[str, Any] = field(default_factory=dict)
    chunk_recommendation: str = "preserve" # preserve, merge, split, overlap

    previous_heading: Optional[str] = None
    current_heading: Optional[str] = None
    next_heading: Optional[str] = None
    section_path: List[str] = field(default_factory=list)
    heading_path: List[str] = field(default_factory=list)
    document_path: List[str] = field(default_factory=list)
    language: str = "en"
    metadata_snapshot: Dict[str, Any] = field(default_factory=dict)

    # Identity & Lineage & Quality (10.2C Revision)
    boundary_hash: str = ""
    boundary_signature: str = ""
    boundary_version: str = "1.0"
    generated_from_rules: List[str] = field(default_factory=list)
    generated_from_nodes: List[str] = field(default_factory=list)
    generated_from_metadata: Dict[str, Any] = field(default_factory=dict)

    quality_score: float = 0.50
    quality_breakdown: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "previous_unit_id": str(self.previous_unit_id) if self.previous_unit_id else None,
            "next_unit_id": str(self.next_unit_id) if self.next_unit_id else None,
            "page": self.page,
            "line": self.line,
            "char_offset": self.char_offset,
            "boundary_type": self.boundary_type,
            "base_confidence": self.base_confidence,
            "heading_bonus": self.heading_bonus,
            "metadata_bonus": self.metadata_bonus,
            "neighbor_bonus": self.neighbor_bonus,
            "semantic_bonus": self.semantic_bonus,
            "structure_bonus": self.structure_bonus,
            "final_confidence": self.final_confidence,
            "priority": self.priority,
            "reason": self.reason,
            "score_breakdown": self.score_breakdown,
            "metadata": self.metadata,
            
            "matched_rules": self.matched_rules,
            "rejected_rules": self.rejected_rules,
            "confidence_breakdown": self.confidence_breakdown,
            "distance_breakdown": self.distance_breakdown,
            "final_reason": self.final_reason,
            "importance_score": self.importance_score,
            "retrieval_weight": self.retrieval_weight,
            "merge_priority": self.merge_priority,
            "retrieval_hints": self.retrieval_hints,
            "chunk_recommendation": self.chunk_recommendation,
            "previous_heading": self.previous_heading,
            "current_heading": self.current_heading,
            "next_heading": self.next_heading,
            "section_path": self.section_path,
            "heading_path": self.heading_path,
            "document_path": self.document_path,
            "language": self.language,
            "metadata_snapshot": self.metadata_snapshot,
            
            "boundary_hash": self.boundary_hash,
            "boundary_signature": self.boundary_signature,
            "boundary_version": self.boundary_version,
            "generated_from_rules": self.generated_from_rules,
            "generated_from_nodes": self.generated_from_nodes,
            "generated_from_metadata": self.generated_from_metadata,
            "quality_score": self.quality_score,
            "quality_breakdown": self.quality_breakdown
        }
