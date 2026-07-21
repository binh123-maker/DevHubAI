import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class ChunkScore:
    # Basic Scores
    overall_score: float = 0.0
    importance_score: float = 0.0
    cohesion_score: float = 0.0
    semantic_density_score: float = 0.0
    readability_score: float = 0.0
    retrieval_score: float = 0.0

    # Technical Scores
    code_density_score: float = 0.0
    table_density_score: float = 0.0
    formula_density_score: float = 0.0
    heading_relevance_score: float = 0.0
    metadata_quality_score: float = 0.0

    # Identity
    score_hash: str = ""
    score_signature: str = ""
    score_version: str = "1.0"

    # Ranking
    ranking_score: float = 0.0
    ranking_priority: float = 0.0
    retrieval_priority: float = 0.0
    context_priority: float = 0.0

    # Quality
    quality_score: float = 0.0
    quality_breakdown: Dict[str, float] = field(default_factory=dict)

    # Retrieval
    semantic_rank: int = 1
    keyword_rank: int = 1
    metadata_rank: int = 1
    hybrid_rank: int = 1
    recommended_retrieval_mode: str = "SEMANTIC"

    # Classification
    score_level: str = "FAIR"

    # Confidence
    confidence: float = 0.80
    confidence_breakdown: Dict[str, float] = field(default_factory=dict)

    # Explainability
    matched_features: List[str] = field(default_factory=list)
    penalties: List[Dict[str, Any]] = field(default_factory=list)
    bonuses: List[Dict[str, Any]] = field(default_factory=list)
    score_breakdown: Dict[str, float] = field(default_factory=dict)
    explanation: str = ""
    recommendation: str = ""

    # Trace
    scoring_trace: Dict[str, Any] = field(default_factory=dict)
    scoring_inputs: Dict[str, Any] = field(default_factory=dict)
    applied_rules: List[str] = field(default_factory=list)
    ignored_rules: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.score_level:
            self.score_level = self.determine_level(self.overall_score)
        if not self.score_hash:
            self.score_hash = self.calculate_hash()

    @staticmethod
    def determine_level(score: float) -> str:
        if score >= 0.85:
            return "EXCELLENT"
        elif score >= 0.70:
            return "GOOD"
        elif score >= 0.50:
            return "FAIR"
        elif score >= 0.30:
            return "LOW"
        else:
            return "POOR"

    def calculate_hash(self) -> str:
        payload = f"{self.score_signature}-{self.overall_score}-{self.score_version}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_score": self.overall_score,
            "importance_score": self.importance_score,
            "cohesion_score": self.cohesion_score,
            "semantic_density_score": self.semantic_density_score,
            "readability_score": self.readability_score,
            "retrieval_score": self.retrieval_score,
            "code_density_score": self.code_density_score,
            "table_density_score": self.table_density_score,
            "formula_density_score": self.formula_density_score,
            "heading_relevance_score": self.heading_relevance_score,
            "metadata_quality_score": self.metadata_quality_score,
            "score_hash": self.score_hash,
            "score_signature": self.score_signature,
            "score_version": self.score_version,
            "ranking_score": self.ranking_score,
            "ranking_priority": self.ranking_priority,
            "retrieval_priority": self.retrieval_priority,
            "context_priority": self.context_priority,
            "quality_score": self.quality_score,
            "quality_breakdown": self.quality_breakdown,
            "semantic_rank": self.semantic_rank,
            "keyword_rank": self.keyword_rank,
            "metadata_rank": self.metadata_rank,
            "hybrid_rank": self.hybrid_rank,
            "recommended_retrieval_mode": self.recommended_retrieval_mode,
            "score_level": self.score_level,
            "confidence": self.confidence,
            "confidence_breakdown": self.confidence_breakdown,
            "matched_features": self.matched_features,
            "penalties": self.penalties,
            "bonuses": self.bonuses,
            "score_breakdown": self.score_breakdown,
            "explanation": self.explanation,
            "recommendation": self.recommendation,
            "scoring_trace": self.scoring_trace,
            "scoring_inputs": self.scoring_inputs,
            "applied_rules": self.applied_rules,
            "ignored_rules": self.ignored_rules
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def pretty_print(self) -> str:
        return (
            f"=== Chunk Score Detail ===\n"
            f"Signature: {self.score_signature}\n"
            f"Overall Score: {self.overall_score:.2f} ({self.score_level})\n"
            f"Quality Score: {self.quality_score:.2f}\n"
            f"Ranking Score: {self.ranking_score:.2f}\n"
            f"Retrieval Priority: {self.retrieval_priority:.2f}\n"
            f"Recommended Mode: {self.recommended_retrieval_mode}\n"
            f"Explanation: {self.explanation}"
        )
