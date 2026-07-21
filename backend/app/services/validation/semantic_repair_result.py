import hashlib
import json
from dataclasses import dataclass, field
from typing import List, Dict, Any
from app.services.validation.repair_issue import RepairIssue

@dataclass
class SemanticRepairResult:
    repaired_chunks: List[Any] = field(default_factory=list)
    repaired_issues: List[RepairIssue] = field(default_factory=list)
    skipped_repairs: List[Any] = field(default_factory=list)
    failed_repairs: List[Any] = field(default_factory=list)
    
    repair_score: float = 1.0
    repair_quality: float = 1.0
    execution_time: float = 0.0
    
    repair_hash: str = ""
    repair_signature: str = ""
    repair_version: str = "1.0"
    repair_fingerprint: str = ""
    
    repair_confidence: float = 1.0
    repair_health_score: float = 1.0
    
    repair_trace: List[Dict[str, Any]] = field(default_factory=list)
    repair_summary: str = ""
    repair_recommendations: List[str] = field(default_factory=list)

    # Phase 10.5C extended fields
    rescored: bool = False
    revalidated: bool = False
    updated_scores: List[Dict[str, Any]] = field(default_factory=list)
    updated_metadata: Dict[str, Any] = field(default_factory=dict)
    previous_fingerprint: str = ""
    new_fingerprint: str = ""
    overall_confidence: float = 1.0

    def __post_init__(self):
        if not self.repair_hash:
            self.repair_hash = self.calculate_hash()
        if not self.repair_signature:
            self.repair_signature = f"REPAIR_RESULT::{self.repair_version}::{len(self.repaired_issues)}"
        if self.repaired_issues:
            self.repair_confidence = sum(r.confidence for r in self.repaired_issues) / len(self.repaired_issues)
        if not self.repair_summary:
            self.repair_summary = f"Repaired {len(self.repaired_issues)} issues successfully."

    def calculate_hash(self) -> str:
        payload = f"{self.repair_score}-{self.repair_quality}-{len(self.repaired_issues)}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "repaired_chunks": [str(getattr(c, "id", c)) for c in self.repaired_chunks],
            "repaired_issues": [r.to_dict() for r in self.repaired_issues],
            "skipped_repairs": [str(s) for s in self.skipped_repairs],
            "failed_repairs": [str(f) for f in self.failed_repairs],
            "repair_score": self.repair_score,
            "repair_quality": self.repair_quality,
            "execution_time": self.execution_time,
            "repair_hash": self.repair_hash,
            "repair_signature": self.repair_signature,
            "repair_version": self.repair_version,
            "repair_fingerprint": self.repair_fingerprint,
            "repair_confidence": self.repair_confidence,
            "repair_health_score": self.repair_health_score,
            "repair_trace": self.repair_trace,
            "repair_summary": self.repair_summary,
            "repair_recommendations": self.repair_recommendations
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
