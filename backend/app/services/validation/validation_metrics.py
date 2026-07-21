from typing import Dict, Any

class ValidationMetrics:
    def __init__(self):
        self.validation_throughput: float = 0.0
        self.chunks_validated: int = 0
        self.average_validation_score: float = 0.0
        self.average_health_score: float = 0.0
        self.average_retrieval_readiness: float = 0.0
        self.rule_execution_time: float = 0.0
        self.cache_hit_ratio: float = 0.0
        self.repair_candidates: int = 0
        self.critical_issue_ratio: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "validation_throughput": self.validation_throughput,
            "chunks_validated": self.chunks_validated,
            "average_validation_score": self.average_validation_score,
            "average_health_score": self.average_health_score,
            "average_retrieval_readiness": self.average_retrieval_readiness,
            "rule_execution_time": self.rule_execution_time,
            "cache_hit_ratio": self.cache_hit_ratio,
            "repair_candidates": self.repair_candidates,
            "critical_issue_ratio": self.critical_issue_ratio
        }
