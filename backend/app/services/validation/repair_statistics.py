from typing import Dict, Any

class RepairStatistics:
    def __init__(self):
        self.repair_distribution: Dict[str, int] = {}
        self.repair_types: Dict[str, int] = {}
        self.merge_count: int = 0
        self.split_count: int = 0
        self.rebuilt_metadata: int = 0
        self.rebuilt_retrieval_metadata: int = 0
        self.rebuilt_scores: int = 0
        self.repaired_overlaps: int = 0
        self.average_repair_confidence: float = 1.0
        self.average_repair_quality: float = 1.0
        self.execution_statistics: Dict[str, Any] = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "repair_distribution": self.repair_distribution,
            "repair_types": self.repair_types,
            "merge_count": self.merge_count,
            "split_count": self.split_count,
            "rebuilt_metadata": self.rebuilt_metadata,
            "rebuilt_retrieval_metadata": self.rebuilt_retrieval_metadata,
            "rebuilt_scores": self.rebuilt_scores,
            "repaired_overlaps": self.repaired_overlaps,
            "average_repair_confidence": self.average_repair_confidence,
            "average_repair_quality": self.average_repair_quality,
            "execution_statistics": self.execution_statistics
        }
