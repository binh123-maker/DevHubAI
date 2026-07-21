class ChunkBuilderConfiguration:
    def __init__(
        self,
        default_max_tokens: int = 500,
        default_min_tokens: int = 100,
        max_overlap: int = 100,
        enable_boundary_split: bool = True,
        enable_importance_weighting: bool = True,
        enable_overlap: bool = True,
        enable_merge_small_chuks: bool = True, # match typo if any, let's also provide the corrected spelling
        enable_merge_small_chunks: bool = True,
        enable_split_large_chunks: bool = True,
        enable_quality_scoring: bool = True,
        enable_fingerprint: bool = True,
        enable_trace: bool = True,
        enable_validation: bool = True,
        enable_chunk_graph: bool = True,
        enable_replay: bool = True,
        enable_cache: bool = False
    ):
        self.DEFAULT_MAX_TOKENS = default_max_tokens
        self.DEFAULT_MIN_TOKENS = default_min_tokens
        self.MAX_OVERLAP = max_overlap
        self.ENABLE_BOUNDARY_SPLIT = enable_boundary_split
        self.ENABLE_IMPORTANCE_WEIGHTING = enable_importance_weighting
        self.ENABLE_OVERLAP = enable_overlap
        self.ENABLE_MERGE_SMALL_CHUNKS = enable_merge_small_chunks or enable_merge_small_chuks
        self.ENABLE_SPLIT_LARGE_CHUNKS = enable_split_large_chunks
        self.ENABLE_QUALITY_SCORING = enable_quality_scoring
        self.ENABLE_FINGERPRINT = enable_fingerprint
        self.ENABLE_TRACE = enable_trace
        self.ENABLE_VALIDATION = enable_validation
        self.ENABLE_CHUNK_GRAPH = enable_chunk_graph
        self.ENABLE_REPLAY = enable_replay
        self.ENABLE_CACHE = enable_cache
