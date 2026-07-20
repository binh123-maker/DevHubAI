import time
import uuid
from typing import Any, Dict, Optional

class BoundaryEvent:
    def __init__(
        self,
        event_type: str,
        boundary_id: Optional[uuid.UUID],
        boundary_type: str,
        severity: str = "INFO",
        details: str = ""
    ):
        self.timestamp: float = time.time()
        self.event_type: str = event_type
        self.boundary_id: Optional[uuid.UUID] = boundary_id
        self.boundary_type: str = boundary_type
        self.severity: str = severity
        self.details: str = details

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "boundary_id": str(self.boundary_id) if self.boundary_id else None,
            "boundary_type": self.boundary_type,
            "severity": self.severity,
            "details": self.details
        }

class BoundaryDetected(BoundaryEvent):
    def __init__(self, boundary_id: uuid.UUID, boundary_type: str, details: str = ""):
        super().__init__("BoundaryDetected", boundary_id, boundary_type, "INFO", details)

class BoundaryRejected(BoundaryEvent):
    def __init__(self, boundary_id: uuid.UUID, boundary_type: str, details: str = ""):
        super().__init__("BoundaryRejected", boundary_id, boundary_type, "WARNING", details)

class BoundaryMerged(BoundaryEvent):
    def __init__(self, boundary_id: uuid.UUID, boundary_type: str, details: str = ""):
        super().__init__("BoundaryMerged", boundary_id, boundary_type, "INFO", details)

class BoundaryValidated(BoundaryEvent):
    def __init__(self, boundary_id: uuid.UUID, boundary_type: str, details: str = ""):
        super().__init__("BoundaryValidated", boundary_id, boundary_type, "INFO", details)

class BoundaryRepaired(BoundaryEvent):
    def __init__(self, boundary_id: uuid.UUID, boundary_type: str, details: str = ""):
        super().__init__("BoundaryRepaired", boundary_id, boundary_type, "WARNING", details)
