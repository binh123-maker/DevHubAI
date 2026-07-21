import time
import uuid
from typing import Optional, Any, Dict

class ScoreEvent:
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

class ChunkScored(ScoreEvent):
    def __init__(self, chunk_id: uuid.UUID, score: float):
        super().__init__("ChunkScored", chunk_id, f"Scored overall_score: {score:.2f}")

class ChunkBoosted(ScoreEvent):
    def __init__(self, chunk_id: uuid.UUID, bonus_name: str):
        super().__init__("ChunkBoosted", chunk_id, f"Boosted with: {bonus_name}")

class ChunkPenalized(ScoreEvent):
    def __init__(self, chunk_id: uuid.UUID, penalty_name: str):
        super().__init__("ChunkPenalized", chunk_id, f"Penalized with: {penalty_name}")

class ChunkRejected(ScoreEvent):
    def __init__(self, chunk_id: uuid.UUID, reason: str):
        super().__init__("ChunkRejected", chunk_id, f"Rejected reason: {reason}")

class ScoreCalculated(ScoreEvent):
    def __init__(self, chunk_id: uuid.UUID, details: str = ""):
        super().__init__("ScoreCalculated", chunk_id, details)

class ScoreValidationFailed(ScoreEvent):
    def __init__(self, chunk_id: Optional[uuid.UUID], error: str):
        super().__init__("ScoreValidationFailed", chunk_id, f"Validation error: {error}")

# Phase 10.4B+ extended events
class PipelineScoringStarted(ScoreEvent):
    def __init__(self, details: str = ""):
        super().__init__("PipelineScoringStarted", None, details)

class PipelineScoringFinished(ScoreEvent):
    def __init__(self, details: str = ""):
        super().__init__("PipelineScoringFinished", None, details)

class ChunkCached(ScoreEvent):
    def __init__(self, chunk_id: uuid.UUID, details: str = ""):
        super().__init__("ChunkCached", chunk_id, details)

class ChunkCacheHit(ScoreEvent):
    def __init__(self, details: str = ""):
        super().__init__("ChunkCacheHit", None, details)

class ChunkCacheMiss(ScoreEvent):
    def __init__(self, details: str = ""):
        super().__init__("ChunkCacheMiss", None, details)

class ChunkScoreValidationFailed(ScoreEvent):
    def __init__(self, chunk_id: Optional[uuid.UUID], error: str):
        super().__init__("ChunkScoreValidationFailed", chunk_id, error)
