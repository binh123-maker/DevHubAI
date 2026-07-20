import time
import uuid
from typing import Any, Dict, List, Optional
from app.services.semantic.semantic_config import SemanticConfiguration

class SemanticPipelineContext:
    def __init__(
        self,
        document_id: Optional[uuid.UUID] = None,
        document_version_id: Optional[uuid.UUID] = None,
        workspace_id: Optional[uuid.UUID] = None,
        language: str = "en",
        structure_nodes: Optional[List[Any]] = None,
        document_metadata: Optional[Dict[str, Any]] = None,
        semantic_config: Optional[SemanticConfiguration] = None,
        tracing_enabled: bool = True,
        relationship_enabled: bool = True
    ):
        self.document_id = document_id
        self.document_version_id = document_version_id
        self.workspace_id = workspace_id
        
        self.language = language
        self.structure_nodes = structure_nodes or []
        self.document_metadata = document_metadata or {}
        
        self.semantic_config = semantic_config or SemanticConfiguration()
        self.tracing_enabled = tracing_enabled
        self.relationship_enabled = relationship_enabled
        
        # Statistics
        self.processing_start: Optional[float] = time.time()
        self.processing_end: Optional[float] = None
        self.elapsed_time: Optional[float] = None

        # Temporary caches & tracking
        self.semantic_units: List[Any] = []
        self.lookup_maps: Dict[str, Any] = {}
        self.heading_cache: Dict[str, Any] = {}
        
        self.events: List[Any] = []
        self.traces: Dict[uuid.UUID, Any] = {} # Map unit_id to ClassificationTrace

    def start_timer(self):
        self.processing_start = time.time()

    def end_timer(self):
        self.processing_end = time.time()
        if self.processing_start:
            self.elapsed_time = self.processing_end - self.processing_start
        else:
            self.elapsed_time = 0.0
