from typing import Dict, Any

class ScoringMetrics:
    def __init__(self):
        self.total_chunks_scored: int = 0
        self.average_overall_score: float = 0.0
        self.average_quality_score: float = 0.0
        self.average_ranking_score: float = 0.0
        self.average_context_priority: float = 0.0
        self.average_retrieval_priority: float = 0.0
        
        self.average_execution_time: float = 0.0
        self.chunks_per_second: float = 0.0
        self.pipeline_time: float = 0.0
        self.cache_hit_ratio: float = 0.0
        self.peak_memory: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_chunks_scored": self.total_chunks_scored,
            "average_overall_score": self.average_overall_score,
            "average_quality_score": self.average_quality_score,
            "average_ranking_score": self.average_ranking_score,
            "average_context_priority": self.average_context_priority,
            "average_retrieval_priority": self.average_retrieval_priority,
            "average_execution_time": self.average_execution_time,
            "chunks_per_second": self.chunks_per_second,
            "pipeline_time": self.pipeline_time,
            "cache_hit_ratio": self.cache_hit_ratio,
            "peak_memory": self.peak_memory
        }
