from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class ScoringProfile:
    importance_weight: float = 0.20
    cohesion_weight: float = 0.15
    semantic_density_weight: float = 0.10
    code_density_weight: float = 0.10
    table_density_weight: float = 0.10
    formula_density_weight: float = 0.05
    heading_relevance_weight: float = 0.10
    metadata_quality_weight: float = 0.10
    readability_weight: float = 0.10
    retrieval_weight: float = 0.10
    
    minimum_quality_score: float = 0.40
    scoring_version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "importance_weight": self.importance_weight,
            "cohesion_weight": self.cohesion_weight,
            "semantic_density_weight": self.semantic_density_weight,
            "code_density_weight": self.code_density_weight,
            "table_density_weight": self.table_density_weight,
            "formula_density_weight": self.formula_density_weight,
            "heading_relevance_weight": self.heading_relevance_weight,
            "metadata_quality_weight": self.metadata_quality_weight,
            "readability_weight": self.readability_weight,
            "retrieval_weight": self.retrieval_weight,
            "minimum_quality_score": self.minimum_quality_score,
            "scoring_version": self.scoring_version
        }
