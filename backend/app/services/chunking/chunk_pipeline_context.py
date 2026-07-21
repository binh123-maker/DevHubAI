import time
from typing import Dict, Any, List, Optional
from app.services.chunking.chunk_builder_config import ChunkBuilderConfiguration
from app.services.chunking.chunk_statistics import ChunkStatistics
from app.services.chunking.chunk_metrics import ChunkMetrics

class ChunkPipelineContext:
    def __init__(
        self,
        document_version_id: Optional[Any] = None,
        workspace_id: Optional[Any] = None,
        config: Optional[ChunkBuilderConfiguration] = None
    ):
        self.document_version_id = document_version_id
        self.workspace_id = workspace_id
        self.configuration = config or ChunkBuilderConfiguration()
        self.runtime_caches: Dict[str, Any] = {}
        self.metrics = ChunkMetrics()
        self.statistics = ChunkStatistics()
        self.events: List[Any] = []
        self.reports: List[Any] = []
        self.graph: Optional[Any] = None
        self.validation: Optional[Any] = None
        self.timers: Dict[str, float] = {}

    def start_timer(self, name: str) -> None:
        self.timers[name] = time.time()

    def stop_timer(self, name: str) -> float:
        start = self.timers.get(name)
        if start:
            duration = time.time() - start
            return duration
        return 0.0
