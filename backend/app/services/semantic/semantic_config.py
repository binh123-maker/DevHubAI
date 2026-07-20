class SemanticConfiguration:
    def __init__(
        self,
        min_confidence: float = 0.0,
        default_importance: float = 0.5,
        max_context_window: int = 3,
        enable_trace: bool = True,
        enable_relationships: bool = True,
        enable_neighbor_scan: bool = True,
        enable_metadata_reuse: bool = True,
        enable_context_classification: bool = True,
        default_language: str = "en"
    ):
        self.MIN_CONFIDENCE = min_confidence
        self.DEFAULT_IMPORTANCE = default_importance
        self.MAX_CONTEXT_WINDOW = max_context_window
        self.ENABLE_TRACE = enable_trace
        self.ENABLE_RELATIONSHIPS = enable_relationships
        self.ENABLE_NEIGHBOR_SCAN = enable_neighbor_scan
        self.ENABLE_METADATA_REUSE = enable_metadata_reuse
        self.ENABLE_CONTEXT_CLASSIFICATION = enable_context_classification
        self.DEFAULT_LANGUAGE = default_language
