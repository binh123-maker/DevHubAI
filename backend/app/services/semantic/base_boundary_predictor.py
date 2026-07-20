from abc import ABC, abstractmethod
from typing import List, Optional, Any
from app.services.semantic.semantic_unit import SemanticUnit
from app.services.semantic.semantic_boundary import SemanticBoundary
from app.services.semantic.semantic_pipeline_context import SemanticPipelineContext

class BaseBoundaryPredictor(ABC):
    @abstractmethod
    def predict_boundaries(
        self,
        units: List[SemanticUnit],
        context: Optional[SemanticPipelineContext] = None
    ) -> List[SemanticBoundary]:
        """
        Evaluate semantic units and predict transition boundary maps.
        """
        pass
