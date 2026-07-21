import time
import uuid
from typing import Any, Dict, Optional

class ChunkEvent:
    def __init__(
        self,
        event_type: str,
        chunk_id: Optional[uuid.UUID],
        severity: str = "INFO",
        details: str = ""
    ):
        self.timestamp: float = time.time()
        self.event_type: str = event_type
        self.chunk_id: Optional[uuid.UUID] = chunk_id
        self.severity: str = severity
        self.details: str = details

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "chunk_id": str(self.chunk_id) if self.chunk_id else None,
            "severity": self.severity,
            "details": self.details
        }

class ChunkCreated(ChunkEvent):
    def __init__(self, chunk_id: uuid.UUID, details: str = ""):
        super().__init__("ChunkCreated", chunk_id, "INFO", details)

class ChunkMerged(ChunkEvent):
    def __init__(self, chunk_id: uuid.UUID, details: str = ""):
        super().__init__("ChunkMerged", chunk_id, "INFO", details)

class ChunkSplit(ChunkEvent):
    def __init__(self, chunk_id: uuid.UUID, details: str = ""):
        super().__init__("ChunkSplit", chunk_id, "INFO", details)

class ChunkValidated(ChunkEvent):
    def __init__(self, chunk_id: uuid.UUID, details: str = ""):
        super().__init__("ChunkValidated", chunk_id, "INFO", details)

class ChunkCached(ChunkEvent):
    def __init__(self, chunk_id: uuid.UUID, details: str = ""):
        super().__init__("ChunkCached", chunk_id, "INFO", details)

class ChunkExported(ChunkEvent):
    def __init__(self, chunk_id: uuid.UUID, details: str = ""):
        super().__init__("ChunkExported", chunk_id, "INFO", details)

# 10.3D extended events
class ChunkOptimized(ChunkEvent):
    def __init__(self, chunk_id: uuid.UUID, details: str = ""):
        super().__init__("ChunkOptimized", chunk_id, "INFO", details)

class ChunkCacheHit(ChunkEvent):
    def __init__(self, details: str = ""):
        super().__init__("ChunkCacheHit", None, "INFO", details)

class ChunkCacheMiss(ChunkEvent):
    def __init__(self, details: str = ""):
        super().__init__("ChunkCacheMiss", None, "INFO", details)

class ChunkReplayStarted(ChunkEvent):
    def __init__(self, details: str = ""):
        super().__init__("ChunkReplayStarted", None, "INFO", details)

class ChunkReplayFinished(ChunkEvent):
    def __init__(self, details: str = ""):
        super().__init__("ChunkReplayFinished", None, "INFO", details)

class ChunkOptimizationCompleted(ChunkEvent):
    def __init__(self, details: str = ""):
        super().__init__("ChunkOptimizationCompleted", None, "INFO", details)

class ChunkPipelineFinished(ChunkEvent):
    def __init__(self, details: str = ""):
        super().__init__("ChunkPipelineFinished", None, "INFO", details)
