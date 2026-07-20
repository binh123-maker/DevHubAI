import time
import uuid
from typing import Any, Dict, Optional

class SemanticEvent:
    def __init__(
        self,
        event_type: str,
        semantic_unit_id: Optional[uuid.UUID],
        document_version_id: Optional[uuid.UUID],
        details: str = "",
        severity: str = "INFO"
    ):
        self.timestamp: float = time.time()
        self.event_type: str = event_type
        self.semantic_unit_id: Optional[uuid.UUID] = semantic_unit_id
        self.document_version_id: Optional[uuid.UUID] = document_version_id
        self.details: str = details
        self.severity: str = severity

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "semantic_unit_id": str(self.semantic_unit_id) if self.semantic_unit_id else None,
            "document_version_id": str(self.document_version_id) if self.document_version_id else None,
            "details": self.details,
            "severity": self.severity
        }

class SemanticDetected(SemanticEvent):
    def __init__(self, semantic_unit_id: uuid.UUID, document_version_id: uuid.UUID, details: str = ""):
        super().__init__("SemanticDetected", semantic_unit_id, document_version_id, details, "INFO")

class SemanticRejected(SemanticEvent):
    def __init__(self, semantic_unit_id: uuid.UUID, document_version_id: uuid.UUID, details: str = ""):
        super().__init__("SemanticRejected", semantic_unit_id, document_version_id, details, "WARNING")

class SemanticMerged(SemanticEvent):
    def __init__(self, semantic_unit_id: uuid.UUID, document_version_id: uuid.UUID, details: str = ""):
        super().__init__("SemanticMerged", semantic_unit_id, document_version_id, details, "INFO")

class SemanticSplit(SemanticEvent):
    def __init__(self, semantic_unit_id: uuid.UUID, document_version_id: uuid.UUID, details: str = ""):
        super().__init__("SemanticSplit", semantic_unit_id, document_version_id, details, "INFO")

class SemanticValidated(SemanticEvent):
    def __init__(self, semantic_unit_id: uuid.UUID, document_version_id: uuid.UUID, details: str = ""):
        super().__init__("SemanticValidated", semantic_unit_id, document_version_id, details, "INFO")

class SemanticRepair(SemanticEvent):
    def __init__(self, semantic_unit_id: uuid.UUID, document_version_id: uuid.UUID, details: str = ""):
        super().__init__("SemanticRepair", semantic_unit_id, document_version_id, details, "WARNING")
