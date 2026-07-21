import time
import uuid
from typing import Optional, Any, Dict

class ValidationEvent:
    def __init__(self, event_type: str, chunk_id: Optional[uuid.UUID], details: str = ""):
        self.timestamp: float = time.time()
        self.event_type: str = event_type
        self.chunk_id: Optional[uuid.UUID] = chunk_id
        self.details: str = details

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "chunk_id": str(self.chunk_id) if self.chunk_id else None,
            "details": self.details
        }

class PipelineValidationStarted(ValidationEvent):
    def __init__(self, details: str = ""):
        super().__init__("PipelineValidationStarted", None, details)

class PipelineValidationFinished(ValidationEvent):
    def __init__(self, details: str = ""):
        super().__init__("PipelineValidationFinished", None, details)

class ChunkScoreValidationFailed(ValidationEvent):
    def __init__(self, chunk_id: Optional[uuid.UUID], error: str):
        super().__init__("ChunkScoreValidationFailed", chunk_id, error)

# Phase 10.5C Pipeline Events
class RepairPipelineStarted(ValidationEvent):
    def __init__(self, details: str = ""):
        super().__init__("RepairPipelineStarted", None, details)

class RepairPipelineFinished(ValidationEvent):
    def __init__(self, details: str = ""):
        super().__init__("RepairPipelineFinished", None, details)

class ChunkRepairSkipped(ValidationEvent):
    def __init__(self, chunk_id: uuid.UUID, reason: str = ""):
        super().__init__("ChunkRepairSkipped", chunk_id, reason)

class ChunkRepairSucceeded(ValidationEvent):
    def __init__(self, chunk_id: uuid.UUID, details: str = ""):
        super().__init__("ChunkRepairSucceeded", chunk_id, details)

class ChunkRepairFailed(ValidationEvent):
    def __init__(self, chunk_id: uuid.UUID, error: str = ""):
        super().__init__("ChunkRepairFailed", chunk_id, error)

class PipelineRecovered(ValidationEvent):
    def __init__(self, details: str = ""):
        super().__init__("PipelineRecovered", None, details)

class PipelineFallback(ValidationEvent):
    def __init__(self, details: str = ""):
        super().__init__("PipelineFallback", None, details)

class ChunkValidated(ValidationEvent):
    def __init__(self, chunk_id: uuid.UUID, score: float):
        super().__init__("ChunkValidated", chunk_id, f"Validation score: {score:.2f}")

class ChunkRejected(ValidationEvent):
    def __init__(self, chunk_id: uuid.UUID, reason: str):
        super().__init__("ChunkRejected", chunk_id, reason)

class ValidationCacheHit(ValidationEvent):
    def __init__(self, details: str = ""):
        super().__init__("ValidationCacheHit", None, details)

class ValidationCacheMiss(ValidationEvent):
    def __init__(self, details: str = ""):
        super().__init__("ValidationCacheMiss", None, details)

class ValidationRuleExecuted(ValidationEvent):
    def __init__(self, chunk_id: uuid.UUID, rule_name: str):
        super().__init__("ValidationRuleExecuted", chunk_id, f"Executed: {rule_name}")

class RepairSuggested(ValidationEvent):
    def __init__(self, chunk_id: uuid.UUID, hint: str):
        super().__init__("RepairSuggested", chunk_id, hint)

class RepairSkipped(ValidationEvent):
    def __init__(self, chunk_id: uuid.UUID, details: str = ""):
        super().__init__("RepairSkipped", chunk_id, details)

class CriticalIssueDetected(ValidationEvent):
    def __init__(self, chunk_id: uuid.UUID, issue_type: str):
        super().__init__("CriticalIssueDetected", chunk_id, issue_type)
