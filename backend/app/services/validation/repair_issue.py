import uuid
import time
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

@dataclass
class RepairIssue:
    repair_type: str
    repair_strategy: str
    severity: str
    affected_chunk: uuid.UUID
    before_state: str
    after_state: str
    confidence: float
    repair_reason: str
    
    repair_id: uuid.UUID = field(default_factory=uuid.uuid4)
    repair_hash: str = ""
    repair_signature: str = ""
    source_issue: Optional[Any] = None
    affected_units: List[uuid.UUID] = field(default_factory=list)
    execution_time: float = 0.0

    def __post_init__(self):
        if not self.repair_hash:
            self.repair_hash = self.calculate_hash()
        if not self.repair_signature:
            self.repair_signature = f"REPAIR::{self.repair_type.upper()}::{self.repair_strategy.upper()}"

    def calculate_hash(self) -> str:
        payload = f"{self.affected_chunk}-{self.repair_type}-{self.repair_strategy}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "repair_id": str(self.repair_id),
            "repair_hash": self.repair_hash,
            "repair_signature": self.repair_signature,
            "repair_type": self.repair_type,
            "repair_strategy": self.repair_strategy,
            "severity": self.severity,
            "source_issue": str(self.source_issue) if self.source_issue else None,
            "affected_chunk": str(self.affected_chunk),
            "affected_units": [str(u) for u in self.affected_units],
            "before_state": self.before_state,
            "after_state": self.after_state,
            "confidence": self.confidence,
            "repair_reason": self.repair_reason,
            "execution_time": self.execution_time
        }
