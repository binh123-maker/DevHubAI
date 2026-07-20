from typing import Dict, Any

class SemanticMetrics:
    def __init__(self):
        self.total_nodes: int = 0
        self.total_units: int = 0
        self.semantic_distribution: Dict[str, int] = {
            "definition": 0,
            "example": 0,
            "warning": 0,
            "tip": 0,
            "summary": 0,
            "algorithm": 0,
            "code_example": 0,
            "table": 0,
            "formula": 0,
            "question": 0,
            "answer": 0,
            "paragraph": 0
        }
        self.average_confidence: float = 0.0
        self.average_importance: float = 0.0
        self.processing_time: float = 0.0
        self.classification_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_nodes": self.total_nodes,
            "total_units": self.total_units,
            "semantic_distribution": self.semantic_distribution,
            "average_confidence": self.average_confidence,
            "average_importance": self.average_importance,
            "processing_time": self.processing_time,
            "classification_time": self.classification_time
        }

    def summary(self) -> str:
        return (
            f"Processed {self.total_nodes} nodes into {self.total_units} units. "
            f"Avg Confidence: {self.average_confidence:.2f}, Avg Importance: {self.average_importance:.2f}. "
            f"Processing Time: {self.processing_time * 1000:.2f}ms"
        )

    def pretty_print(self) -> str:
        dist = ", ".join([f"{k}: {v}" for k, v in self.semantic_distribution.items() if v > 0])
        return (
            f"=== Semantic Processing Metrics ===\n"
            f"Total Nodes: {self.total_nodes}\n"
            f"Total Units: {self.total_units}\n"
            f"Distribution: {dist if dist else 'None'}\n"
            f"Average Confidence: {self.average_confidence:.4f}\n"
            f"Average Importance: {self.average_importance:.4f}\n"
            f"Processing Time: {self.processing_time * 1000:.2f}ms\n"
            f"Classification Time: {self.classification_time * 1000:.2f}ms"
        )
