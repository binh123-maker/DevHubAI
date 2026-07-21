import uuid
import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from app.services.semantic.semantic_unit import SemanticUnit
from app.services.semantic.semantic_boundary import SemanticBoundary

@dataclass
class SemanticChunk:
    # Basic Fields
    id: uuid.UUID
    document_version_id: Optional[uuid.UUID]
    workspace_id: Optional[uuid.UUID]
    chunk_index: int

    # Content
    semantic_units: List[SemanticUnit]
    semantic_boundaries: List[SemanticBoundary]
    content: str
    language: str

    # Hierarchy & Context Snapshot
    heading_path: List[str]
    section_path: List[str]
    document_path: List[str]
    metadata_snapshot: Dict[str, Any] = field(default_factory=dict)

    # Scores & Retrieval Metadata
    importance_score: float = 0.50
    retrieval_weight: float = 1.0
    quality_score: float = 0.80
    quality_breakdown: Dict[str, float] = field(default_factory=dict)
    
    retrieval_hints: Dict[str, Any] = field(default_factory=dict)
    recommended_search_modes: List[str] = field(default_factory=list)
    embedding_ready: bool = True
    semantic_search_score: float = 0.0
    metadata_search_score: float = 0.0
    fulltext_search_score: float = 0.0

    # Size Estimation
    estimated_tokens: int = 0
    estimated_words: int = 0
    estimated_characters: int = 0

    # Overlaps
    overlap_before: str = ""
    overlap_after: str = ""

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Identity
    chunk_hash: str = ""
    chunk_signature: str = ""
    chunk_version: str = "1.0"
    fingerprint: str = ""

    # Lineage
    generated_from_units: List[str] = field(default_factory=list)
    generated_from_boundaries: List[str] = field(default_factory=list)
    generated_from_headings: List[str] = field(default_factory=list)
    generated_from_sections: List[str] = field(default_factory=list)
    source_metadata: Dict[str, Any] = field(default_factory=dict)
    creation_strategy: str = "adaptive_semantic"
    source_structure_nodes: List[str] = field(default_factory=list)
    source_boundary_ids: List[str] = field(default_factory=list)
    parent_chunk_id: Optional[uuid.UUID] = None

    # Explainability
    creation_reason: str = ""
    merge_reason: str = ""
    split_reason: str = ""
    retrieval_reason: str = ""
    semantic_reason: str = ""
    quality_reason: str = ""
    creation_trace: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.chunk_hash:
            self.chunk_hash = self.calculate_hash()
        if not self.fingerprint:
            self.fingerprint = self.calculate_fingerprint()
        if not self.chunk_signature:
            self.chunk_signature = self.generate_signature()

    def calculate_hash(self) -> str:
        # SHA-256 generated from: document_version_id, chunk_index, semantic unit ids, heading_path
        unit_ids = "-".join([str(u.id) for u in self.semantic_units])
        hpath = "/".join(self.heading_path)
        payload = f"{self.document_version_id}-{self.chunk_index}-{unit_ids}-{hpath}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def calculate_fingerprint(self) -> str:
        unit_ids = "-".join([str(u.id) for u in self.semantic_units])
        boundary_ids = "-".join([str(b.id) for b in self.semantic_boundaries])
        payload = f"{unit_ids}|{boundary_ids}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def generate_signature(self) -> str:
        h_part = self.heading_path[-1].upper().replace(" ", "_") if self.heading_path else "DOCUMENT"
        s_part = self.section_path[-1].upper().replace(" ", "_") if self.section_path else "SECTION"
        return f"{h_part}::{s_part}::CHUNK_{self.chunk_index}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "document_version_id": str(self.document_version_id) if self.document_version_id else None,
            "workspace_id": str(self.workspace_id) if self.workspace_id else None,
            "chunk_index": self.chunk_index,
            "content": self.content,
            "language": self.language,
            "heading_path": self.heading_path,
            "section_path": self.section_path,
            "document_path": self.document_path,
            "metadata_snapshot": self.metadata_snapshot,
            "importance_score": self.importance_score,
            "retrieval_weight": self.retrieval_weight,
            "quality_score": self.quality_score,
            "quality_breakdown": self.quality_breakdown,
            "retrieval_hints": self.retrieval_hints,
            "recommended_search_modes": self.recommended_search_modes,
            "embedding_ready": self.embedding_ready,
            "semantic_search_score": self.semantic_search_score,
            "metadata_search_score": self.metadata_search_score,
            "fulltext_search_score": self.fulltext_search_score,
            "estimated_tokens": self.estimated_tokens,
            "estimated_words": self.estimated_words,
            "estimated_characters": self.estimated_characters,
            "overlap_before": self.overlap_before,
            "overlap_after": self.overlap_after,
            "metadata": self.metadata,
            "chunk_hash": self.chunk_hash,
            "chunk_signature": self.chunk_signature,
            "chunk_version": self.chunk_version,
            "fingerprint": self.fingerprint,
            "generated_from_units": self.generated_from_units,
            "generated_from_boundaries": self.generated_from_boundaries,
            "generated_from_headings": self.generated_from_headings,
            "generated_from_sections": self.generated_from_sections,
            "source_metadata": self.source_metadata,
            "creation_strategy": self.creation_strategy,
            "source_structure_nodes": self.source_structure_nodes,
            "source_boundary_ids": self.source_boundary_ids,
            "parent_chunk_id": str(self.parent_chunk_id) if self.parent_chunk_id else None,
            "creation_reason": self.creation_reason,
            "merge_reason": self.merge_reason,
            "split_reason": self.split_reason,
            "retrieval_reason": self.retrieval_reason,
            "semantic_reason": self.semantic_reason,
            "quality_reason": self.quality_reason,
            "creation_trace": self.creation_trace
        }
