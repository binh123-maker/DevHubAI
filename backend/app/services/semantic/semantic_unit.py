import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class SemanticUnit:
    # Basic Information
    id: uuid.UUID
    structure_node_id: uuid.UUID
    semantic_type: str
    content: str
    language: Optional[str] = None

    # Scoring
    semantic_confidence: float = 1.0
    importance_score: float = 0.5
    estimated_tokens: int = 0

    # Structural Relationships
    previous_unit_id: Optional[uuid.UUID] = None
    next_unit_id: Optional[uuid.UUID] = None
    parent_heading_id: Optional[uuid.UUID] = None

    # Inherited Structure Metadata
    heading_path: List[str] = field(default_factory=list)
    section_path: List[str] = field(default_factory=list)
    document_path: List[str] = field(default_factory=list)

    # Source Location
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    char_start: Optional[int] = None
    char_end: Optional[int] = None

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert SemanticUnit to dictionary for serialization and compatibility."""
        return {
            "id": str(self.id),
            "structure_node_id": str(self.structure_node_id),
            "semantic_type": self.semantic_type,
            "content": self.content,
            "language": self.language,
            "semantic_confidence": self.semantic_confidence,
            "importance_score": self.importance_score,
            "estimated_tokens": self.estimated_tokens,
            "previous_unit_id": str(self.previous_unit_id) if self.previous_unit_id else None,
            "next_unit_id": str(self.next_unit_id) if self.next_unit_id else None,
            "parent_heading_id": str(self.parent_heading_id) if self.parent_heading_id else None,
            "heading_path": self.heading_path,
            "section_path": self.section_path,
            "document_path": self.document_path,
            "page_start": self.page_start,
            "page_end": self.page_end,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "char_start": self.char_start,
            "char_end": self.char_end,
            "metadata": self.metadata,
        }
