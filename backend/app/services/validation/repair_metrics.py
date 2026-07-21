from typing import Dict, Any

class RepairMetrics:
    def __init__(self):
        self.average_repair_time: float = 0.0
        self.average_repair_confidence: float = 1.0
        self.average_repair_quality: float = 1.0
        self.repairs_per_second: float = 0.0
        self.retry_counts: int = 0
        self.validator_execution_time: float = 0.0
        self.strategy_execution_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "average_repair_time": self.average_repair_time,
            "average_repair_confidence": self.average_repair_confidence,
            "average_repair_quality": self.average_repair_quality,
            "repairs_per_second": self.repairs_per_second,
            "retry_counts": self.retry_counts,
            "validator_execution_time": self.validator_execution_time,
            "strategy_execution_time": self.strategy_execution_time
        }
