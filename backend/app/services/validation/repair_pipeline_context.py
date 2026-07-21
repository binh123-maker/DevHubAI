import time
from typing import List, Dict, Any, Optional
from app.services.validation.semantic_repair_profile import SemanticRepairProfile
from app.services.validation.repair_strategy import BaseRepairStrategy

class RepairPipelineContext:
    def __init__(
        self,
        profile: Optional[SemanticRepairProfile] = None,
        strategy: Optional[BaseRepairStrategy] = None,
        validation_result: Optional[Any] = None
    ):
        self.profile: SemanticRepairProfile = profile or SemanticRepairProfile()
        self.strategy: Optional[BaseRepairStrategy] = strategy
        self.validation_result: Optional[Any] = validation_result
        
        self.execution_time: float = 0.0
        self.repaired_chunks: List[Any] = []
        self.repaired_issues: List[Any] = []
        self.retry_counter: int = 0
        
        from app.services.validation.repair_metrics import RepairMetrics
        from app.services.validation.repair_statistics import RepairStatistics
        from app.services.validation.repair_cache import RepairCache
        
        self.metrics: RepairMetrics = RepairMetrics()
        self.statistics: RepairStatistics = RepairStatistics()
        self.cache: RepairCache = RepairCache()
        self.events: List[Any] = []
