from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class SemanticValidationProfile:
    minimum_overall_score: float = 0.40
    minimum_quality_score: float = 0.40
    minimum_semantic_density: float = 0.10
    minimum_cohesion: float = 0.40
    minimum_heading_relevance: float = 0.30
    minimum_metadata_richness: float = 0.10
    minimum_language_confidence: float = 0.50
    maximum_overlap_ratio: float = 0.35
    maximum_duplicate_similarity: float = 0.85
    maximum_chunk_tokens: int = 1000
    minimum_chunk_tokens: int = 10
    allow_cross_heading: bool = False
    allow_cross_section: bool = False
    allow_invalid_retrieval_metadata: bool = False
    strict_mode: bool = False
    validation_version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "minimum_overall_score": self.minimum_overall_score,
            "minimum_quality_score": self.minimum_quality_score,
            "minimum_semantic_density": self.minimum_semantic_density,
            "minimum_cohesion": self.minimum_cohesion,
            "minimum_heading_relevance": self.minimum_heading_relevance,
            "minimum_metadata_richness": self.minimum_metadata_richness,
            "minimum_language_confidence": self.minimum_language_confidence,
            "maximum_overlap_ratio": self.maximum_overlap_ratio,
            "maximum_duplicate_similarity": self.maximum_duplicate_similarity,
            "maximum_chunk_tokens": self.maximum_chunk_tokens,
            "minimum_chunk_tokens": self.minimum_chunk_tokens,
            "allow_cross_heading": self.allow_cross_heading,
            "allow_cross_section": self.allow_cross_section,
            "allow_invalid_retrieval_metadata": self.allow_invalid_retrieval_metadata,
            "strict_mode": self.strict_mode,
            "validation_version": self.validation_version
        }
