import uuid
import time
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

@dataclass
class ValidationIssue:
    severity: str  # INFO, WARNING, ERROR, CRITICAL
    category: str  # Structural, Semantic, Boundary, Retrieval, Quality
    subcategory: str
    rule_name: str
    affected_chunk: uuid.UUID
    description: str
    recommendation: str
    repair_hint: str
    
    issue_id: uuid.UUID = field(default_factory=uuid.uuid4)
    issue_hash: str = ""
    issue_signature: str = ""
    affected_units: List[uuid.UUID] = field(default_factory=list)
    location: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.90
    repair_priority: int = 1
    created_at: float = field(default_factory=time.time)

    def __post_init__(self):
        if not self.issue_hash:
            self.issue_hash = self.calculate_hash()
        if not self.issue_signature:
            self.issue_signature = f"{self.category.upper()}::{self.subcategory.upper()}::{self.rule_name}"

    def calculate_hash(self) -> str:
        payload = f"{self.affected_chunk}-{self.rule_name}-{self.category}-{self.severity}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "issue_id": str(self.issue_id),
            "issue_hash": self.issue_hash,
            "issue_signature": self.issue_signature,
            "severity": self.severity,
            "category": self.category,
            "subcategory": self.subcategory,
            "rule_name": self.rule_name,
            "affected_chunk": str(self.affected_chunk),
            "affected_units": [str(u) for u in self.affected_units],
            "location": self.location,
            "confidence": self.confidence,
            "description": self.description,
            "recommendation": self.recommendation,
            "repair_hint": self.repair_hint,
            "repair_priority": self.repair_priority,
            "created_at": self.created_at
        }
