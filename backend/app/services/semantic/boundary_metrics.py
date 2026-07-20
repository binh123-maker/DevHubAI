from typing import Dict, Any

class BoundaryMetrics:
    def __init__(self):
        self.total_boundaries: int = 0
        self.heading_boundaries: int = 0
        self.section_boundaries: int = 0
        self.topic_shift_boundaries: int = 0
        self.code_boundaries: int = 0
        self.table_boundaries: int = 0
        self.formula_boundaries: int = 0
        self.average_confidence: float = 0.0
        self.average_distance: float = 0.0
        self.boundary_density: float = 0.0
        self.processing_time: float = 0.0

        # Extended metrics for 10.2B / 10.2C
        self.boundary_distribution: Dict[str, int] = {}
        self.rule_hit_distribution: Dict[str, int] = {}
        self.execution_time_per_rule: Dict[str, float] = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_boundaries": self.total_boundaries,
            "heading_boundaries": self.heading_boundaries,
            "section_boundaries": self.section_boundaries,
            "topic_shift_boundaries": self.topic_shift_boundaries,
            "code_boundaries": self.code_boundaries,
            "table_boundaries": self.table_boundaries,
            "formula_boundaries": self.formula_boundaries,
            "average_confidence": self.average_confidence,
            "average_distance": self.average_distance,
            "boundary_density": self.boundary_density,
            "processing_time": self.processing_time,
            
            "boundary_distribution": self.boundary_distribution,
            "rule_hit_distribution": self.rule_hit_distribution,
            "execution_time_per_rule": self.execution_time_per_rule
        }

    def summary(self) -> str:
        return (
            f"Detected {self.total_boundaries} boundaries. "
            f"Avg Confidence: {self.average_confidence:.2f}, Avg Distance: {self.average_distance:.2f}. "
            f"Density: {self.boundary_density:.2f}"
        )

    def pretty_print(self) -> str:
        dist = ", ".join([f"{k}: {v}" for k, v in self.boundary_distribution.items() if v > 0])
        hits = ", ".join([f"{k}: {v}" for k, v in self.rule_hit_distribution.items() if v > 0])
        return (
            f"=== Boundary Detection Metrics ===\n"
            f"Total Boundaries: {self.total_boundaries}\n"
            f"Average Confidence: {self.average_confidence:.4f}\n"
            f"Average Distance: {self.average_distance:.4f}\n"
            f"Boundary Density: {self.boundary_density:.4f}\n"
            f"Boundary Type Distribution: {dist if dist else 'None'}\n"
            f"Rule Hit Distribution: {hits if hits else 'None'}\n"
            f"Processing Time: {self.processing_time * 1000:.2f}ms"
        )
