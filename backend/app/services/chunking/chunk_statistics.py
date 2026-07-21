from typing import Dict, Any

class ChunkStatistics:
    def __init__(self):
        self.total_chunks: int = 0
        self.average_chunk_size: float = 0.0
        self.average_tokens: float = 0.0
        self.average_words: float = 0.0
        self.average_overlap: float = 0.0
        self.largest_chunk: int = 0
        self.smallest_chunk: int = 0
        self.importance_distribution: Dict[str, int] = {}
        self.retrieval_distribution: Dict[str, int] = {}
        self.quality_distribution: Dict[str, int] = {}
        self.merge_count: int = 0
        self.split_count: int = 0
        self.execution_time: float = 0.0
        self.memory_usage: float = 0.0

        self.chunk_type_distribution: Dict[str, int] = {}
        self.search_mode_distribution: Dict[str, int] = {}
        self.heading_distribution: Dict[str, int] = {}
        self.code_distribution: Dict[str, int] = {}
        self.table_distribution: Dict[str, int] = {}
        self.formula_distribution: Dict[str, int] = {}

        # 10.3D extended stats
        self.merge_statistics: Dict[str, Any] = {}
        self.split_statistics: Dict[str, Any] = {}
        self.optimization_statistics: Dict[str, Any] = {}
        self.validation_statistics: Dict[str, Any] = {}
        self.cache_statistics: Dict[str, Any] = {}
        self.graph_statistics: Dict[str, Any] = {}
        self.builder_statistics: Dict[str, Any] = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_chunks": self.total_chunks,
            "average_chunk_size": self.average_chunk_size,
            "average_tokens": self.average_tokens,
            "average_words": self.average_words,
            "average_overlap": self.average_overlap,
            "largest_chunk": self.largest_chunk,
            "smallest_chunk": self.smallest_chunk,
            "importance_distribution": self.importance_distribution,
            "retrieval_distribution": self.retrieval_distribution,
            "quality_distribution": self.quality_distribution,
            "merge_count": self.merge_count,
            "split_count": self.split_count,
            "execution_time": self.execution_time,
            "memory_usage": self.memory_usage,
            
            "chunk_type_distribution": self.chunk_type_distribution,
            "search_mode_distribution": self.search_mode_distribution,
            "heading_distribution": self.heading_distribution,
            "code_distribution": self.code_distribution,
            "table_distribution": self.table_distribution,
            "formula_distribution": self.formula_distribution,
            
            "merge_statistics": self.merge_statistics,
            "split_statistics": self.split_statistics,
            "optimization_statistics": self.optimization_statistics,
            "validation_statistics": self.validation_statistics,
            "cache_statistics": self.cache_statistics,
            "graph_statistics": self.graph_statistics,
            "builder_statistics": self.builder_statistics
        }

    def summary(self) -> str:
        return (
            f"Created {self.total_chunks} chunks. Avg Tokens: {self.average_tokens:.2f}, "
            f"Largest: {self.largest_chunk} chars, Smallest: {self.smallest_chunk} chars."
        )

    def pretty_print(self) -> str:
        import_dist = ", ".join([f"{k}: {v}" for k, v in self.importance_distribution.items()])
        quality_dist = ", ".join([f"{k}: {v}" for k, v in self.quality_distribution.items()])
        return (
            f"=== Semantic Chunk Statistics ===\n"
            f"Total Chunks: {self.total_chunks}\n"
            f"Average Chunk Size: {self.average_chunk_size:.2f} chars\n"
            f"Average Tokens: {self.average_tokens:.2f}\n"
            f"Average Words: {self.average_words:.2f}\n"
            f"Largest Chunk: {self.largest_chunk} chars\n"
            f"Smallest Chunk: {self.smallest_chunk} chars\n"
            f"Importance Distribution: {import_dist if import_dist else 'None'}\n"
            f"Quality Distribution: {quality_dist if quality_dist else 'None'}\n"
            f"Merge Count: {self.merge_count} | Split Count: {self.split_count}\n"
            f"Execution Time: {self.execution_time * 1000:.2f}ms"
        )
