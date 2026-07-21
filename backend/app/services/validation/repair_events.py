import time
import uuid
from typing import Optional, Any, Dict

class RepairEvent:
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

class RepairStarted(RepairEvent):
    def __init__(self, details: str = ""):
        super().__init__("RepairStarted", None, details)

class RepairFinished(RepairEvent):
    def __init__(self, details: str = ""):
        super().__init__("RepairFinished", None, details)

class ChunkMerged(RepairEvent):
    def __init__(self, chunk_id: uuid.UUID, merged_into: uuid.UUID):
        super().__init__("ChunkMerged", chunk_id, f"Merged into: {merged_into}")

class ChunkSplit(RepairEvent):
    def __init__(self, chunk_id: uuid.UUID, count: int):
        super().__init__("ChunkSplit", chunk_id, f"Split into {count} sub-chunks")

class MetadataRebuilt(RepairEvent):
    def __init__(self, chunk_id: uuid.UUID, details: str = ""):
        super().__init__("MetadataRebuilt", chunk_id, details)

class RetrievalUpdated(RepairEvent):
    def __init__(self, chunk_id: uuid.UUID, details: str = ""):
        super().__init__("RetrievalUpdated", chunk_id, details)

class RepairSkipped(RepairEvent):
    def __init__(self, chunk_id: uuid.UUID, details: str = ""):
        super().__init__("RepairSkipped", chunk_id, details)

class RepairFailed(RepairEvent):
    def __init__(self, chunk_id: uuid.UUID, error: str):
        super().__init__("RepairFailed", chunk_id, error)

class RevalidationStarted(RepairEvent):
    def __init__(self, details: str = ""):
        super().__init__("RevalidationStarted", None, details)

class RevalidationFinished(RepairEvent):
    def __init__(self, details: str = ""):
        super().__init__("RevalidationFinished", None, details)

# Phase 10.5C Events
class RescoringStarted(RepairEvent):
    def __init__(self, details: str = ""):
        super().__init__("RescoringStarted", None, details)

class RescoringFinished(RepairEvent):
    def __init__(self, details: str = ""):
        super().__init__("RescoringFinished", None, details)

class MetadataUpdated(RepairEvent):
    def __init__(self, chunk_id: uuid.UUID, details: str = ""):
        super().__init__("MetadataUpdated", chunk_id, details)

class RepairHistoryUpdated(RepairEvent):
    def __init__(self, chunk_id: uuid.UUID, details: str = ""):
        super().__init__("RepairHistoryUpdated", chunk_id, details)

class FingerprintChanged(RepairEvent):
    def __init__(self, chunk_id: uuid.UUID, old_fp: str, new_fp: str):
        super().__init__("FingerprintChanged", chunk_id, f"{old_fp} -> {new_fp}")

class PipelineCompleted(RepairEvent):
    def __init__(self, details: str = ""):
        super().__init__("PipelineCompleted", None, details)
