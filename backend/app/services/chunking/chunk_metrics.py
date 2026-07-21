from typing import Dict, Any

class ChunkMetrics:
    def __init__(self):
        self.chunk_creation_time: float = 0.0
        self.merge_time: float = 0.0
        self.split_time: float = 0.0
        self.quality_distribution: Dict[str, int] = {}
        self.importance_distribution: Dict[str, int] = {}
        self.retrieval_distribution: Dict[str, int] = {}
        self.memory_usage: float = 0.0
        self.cache_statistics: Dict[str, Any] = {}

        self.average_code_density: float = 0.0
        self.average_formula_density: float = 0.0
        self.average_table_density: float = 0.0
        self.average_topic_consistency: float = 0.0
        self.average_heading_relevance: float = 0.0
        self.average_boundary_confidence: float = 0.0
        self.average_search_weight: float = 0.0

        # Phase 10.3D extended production metrics
        self.builder_time: float = 0.0
        self.optimizer_time: float = 0.0
        self.validator_time: float = 0.0
        self.cache_time: float = 0.0
        self.report_time: float = 0.0
        self.export_time: float = 0.0
        self.peak_memory: float = 0.0
        self.chunks_per_second: float = 0.0
        self.average_chunk_build_time: float = 0.0
        self.average_optimizer_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_creation_time": self.chunk_creation_time,
            "merge_time": self.merge_time,
            "split_time": self.split_time,
            "quality_distribution": self.quality_distribution,
            "importance_distribution": self.importance_distribution,
            "retrieval_distribution": self.retrieval_distribution,
            "memory_usage": self.memory_usage,
            "cache_statistics": self.cache_statistics,
            
            "average_code_density": self.average_code_density,
            "average_formula_density": self.average_formula_density,
            "average_table_density": self.average_table_density,
            "average_topic_consistency": self.average_topic_consistency,
            "average_heading_relevance": self.average_heading_relevance,
            "average_boundary_confidence": self.average_boundary_confidence,
            "average_search_weight": self.average_search_weight,
            
            "builder_time": self.builder_time,
            "optimizer_time": self.optimizer_time,
            "validator_time": self.validator_time,
            "cache_time": self.cache_time,
            "report_time": self.report_time,
            "export_time": self.export_time,
            "peak_memory": self.peak_memory,
            "chunks_per_second": self.chunks_per_second,
            "average_chunk_build_time": self.average_chunk_build_time,
            "average_optimizer_time": self.average_optimizer_time
        }

    def summary(self) -> str:
        return f"Creation Time: {self.chunk_creation_time*1000:.2f}ms, Builder: {self.average_chunk_build_time*1000:.2f}ms, Optimizer: {self.average_optimizer_time*1000:.2f}ms"

    def pretty_print(self) -> str:
        return (
            f"=== Chunk Pipeline Metrics ===\n"
            f"Creation Time: {self.chunk_creation_time * 1000:.2f}ms\n"
            f"Average Chunk Build Time: {self.average_chunk_build_time*1000:.2f}ms\n"
            f"Average Optimizer Time: {self.average_optimizer_time*1000:.2f}ms\n"
            f"Memory Usage: {self.memory_usage:.2f} KB\n"
            f"Peak Memory: {self.peak_memory:.2f} KB"
        )
