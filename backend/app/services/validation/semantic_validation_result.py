import hashlib
import json
from dataclasses import dataclass, field
from typing import List, Dict, Any
from app.services.validation.validation_issue import ValidationIssue

@dataclass
class SemanticValidationResult:
    validation_hash: str = ""
    validation_version: str = "1.0"
    validator_version: str = "1.0"
    overall_status: str = "VALID"
    overall_validation_score: float = 1.0
    pipeline_health_score: float = 1.0
    retrieval_readiness_score: float = 1.0
    semantic_quality_score: float = 1.0
    total_rules: int = 0
    passed_rules: int = 0
    failed_rules: int = 0
    critical_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    repair_candidates: List[Dict[str, Any]] = field(default_factory=list)
    execution_time: float = 0.0
    validation_trace: List[Dict[str, Any]] = field(default_factory=list)

    # Phase 10.5C extended fields
    repair_performed: bool = False
    repair_success: bool = False
    repair_confidence: float = 1.0
    repair_history: List[Dict[str, Any]] = field(default_factory=list)
    repair_count: int = 0
    pipeline_status: str = "UNVALIDATED"
    overall_health: float = 1.0
    execution_trace: List[Dict[str, Any]] = field(default_factory=list)
    repair_version: str = "1.0"

    def __post_init__(self):
        self.critical_count = sum(1 for i in self.issues if i.severity == "CRITICAL")
        self.warning_count = sum(1 for i in self.issues if i.severity == "WARNING")
        self.info_count = sum(1 for i in self.issues if i.severity == "INFO")
        
        if self.critical_count > 0:
            self.overall_status = "INVALID"
            
        if not self.validation_hash:
            self.validation_hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        payload = f"{self.overall_status}-{self.overall_validation_score}-{len(self.issues)}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "validation_hash": self.validation_hash,
            "validation_version": self.validation_version,
            "validator_version": self.validator_version,
            "overall_status": self.overall_status,
            "overall_validation_score": self.overall_validation_score,
            "pipeline_health_score": self.pipeline_health_score,
            "retrieval_readiness_score": self.retrieval_readiness_score,
            "semantic_quality_score": self.semantic_quality_score,
            "total_rules": self.total_rules,
            "passed_rules": self.passed_rules,
            "failed_rules": self.failed_rules,
            "critical_count": self.critical_count,
            "warning_count": self.warning_count,
            "info_count": self.info_count,
            "issues": [i.to_dict() for i in self.issues],
            "recommendations": self.recommendations,
            "repair_candidates": self.repair_candidates,
            "execution_time": self.execution_time,
            "validation_trace": self.validation_trace
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
