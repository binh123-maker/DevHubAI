import uuid
import pytest
import math
from app.services.chunking.semantic_chunk import SemanticChunk
from app.services.scoring.scoring_profile import ScoringProfile
from app.services.scoring.chunk_score import ChunkScore
from app.services.scoring.chunk_scoring_engine import ChunkScoringEngine
from app.services.scoring.score_explanation_report import ScoreExplanationReport
from app.services.scoring.score_cache import ScoreCache
from app.services.scoring.score_events import ChunkScored, ChunkBoosted, ChunkPenalized, ChunkRejected
from app.services.scoring.scoring_validator import ScoringValidator

def test_score_calculation_and_profile():
    # Setup scoring profile
    profile = ScoringProfile(importance_weight=0.30, cohesion_weight=0.20)
    assert profile.importance_weight == 0.30

    # Setup mock SemanticChunk
    chunk = SemanticChunk(
        id=uuid.uuid4(),
        document_version_id=uuid.uuid4(),
        workspace_id=None,
        chunk_index=0,
        semantic_units=[],
        semantic_boundaries=[],
        content="This is chunk content. It contains some regular text.",
        language="en",
        heading_path=["Chapter 1"],
        section_path=["Section 1"],
        document_path=[],
        importance_score=0.8,
        retrieval_weight=1.5,
        quality_breakdown={
            "semantic_cohesion": 0.90,
            "semantic_density": 0.70,
            "heading_relevance": 0.85
        },
        retrieval_hints={"contains_code": False}
    )

    score = ChunkScoringEngine.score_chunk(chunk, profile)
    
    # Assert deterministic attributes
    assert 0.0 <= score.overall_score <= 1.0
    assert score.score_level in ("EXCELLENT", "GOOD", "FAIR", "LOW", "POOR")
    assert score.ranking_score > 0.0
    assert score.recommended_retrieval_mode == "SEMANTIC"

    # Verify explainability
    report = ScoreExplanationReport(score)
    assert "Overall Score" in report.to_markdown()
    assert isinstance(report.to_json(), str)
    assert "overall_score" in score.to_dict()


def test_penalties_and_bonuses():
    profile = ScoringProfile()

    # Create a very short chunk to trigger ShortContentPenalty
    chunk_short = SemanticChunk(
        id=uuid.uuid4(),
        document_version_id=uuid.uuid4(),
        workspace_id=None,
        chunk_index=0,
        semantic_units=[],
        semantic_boundaries=[],
        content="Short.",
        language="en",
        heading_path=["Chapter 1"],
        section_path=["Section 1"],
        document_path=[],
        importance_score=0.5,
        quality_breakdown={"semantic_cohesion": 0.8, "semantic_density": 0.5, "heading_relevance": 0.5},
        retrieval_hints={}
    )

    score_short = ChunkScoringEngine.score_chunk(chunk_short, profile)
    penalty_names = [p["name"] for p in score_short.penalties]
    assert "short_content_penalty" in penalty_names

    # Create chunk with code to trigger Code bonus and recommended retrieval mode
    chunk_code = SemanticChunk(
        id=uuid.uuid4(),
        document_version_id=uuid.uuid4(),
        workspace_id=None,
        chunk_index=0,
        semantic_units=[],
        semantic_boundaries=[],
        content="def test(): pass",
        language="en",
        heading_path=["Chapter 1"],
        section_path=["Section 1"],
        document_path=[],
        importance_score=0.7,
        quality_breakdown={"semantic_cohesion": 0.8, "semantic_density": 0.5, "heading_relevance": 0.5, "code_density": 0.9},
        retrieval_hints={"contains_code": True}
    )

    score_code = ChunkScoringEngine.score_chunk(chunk_code, profile)
    bonus_names = [b["name"] for b in score_code.bonuses]
    assert "high_code_density" in bonus_names
    assert score_code.recommended_retrieval_mode == "CODE"


def test_score_cache():
    cache = ScoreCache()
    cache.clear()

    profile_hash = "hash_profile"
    fingerprint = "chunk_fp_1"
    version = "1.0"

    assert cache.get(fingerprint, profile_hash, version) is None
    cache.set(fingerprint, profile_hash, version, "mock_score", 0.05)
    
    assert cache.get(fingerprint, profile_hash, version) == "mock_score"
    stats = cache.statistics()
    assert stats["cache_hits"] == 1
    assert stats["hit_ratio"] == 0.5


def test_score_events():
    chunk_id = uuid.uuid4()
    
    evt_scored = ChunkScored(chunk_id, 0.85)
    assert evt_scored.event_type == "ChunkScored"
    assert "0.85" in evt_scored.details

    evt_boosted = ChunkBoosted(chunk_id, "HeadingRelevance")
    assert evt_boosted.event_type == "ChunkBoosted"

    evt_penalized = ChunkPenalized(chunk_id, "ShortContent")
    assert evt_penalized.event_type == "ChunkPenalized"


def test_score_validation():
    # Valid scores list
    score1 = ChunkScore(overall_score=0.8, score_signature="SIG_1", explanation="Good content", recommendation="GOOD_FOR_RETRIEVAL", quality_breakdown={"cohesion": 0.8})
    score2 = ChunkScore(overall_score=0.9, score_signature="SIG_2", explanation="Excellent content", recommendation="GOOD_FOR_RETRIEVAL", quality_breakdown={"cohesion": 0.9})

    report = ScoringValidator.validate([score1, score2])
    assert report.is_valid

    # Duplicate signatures
    score_dup = ChunkScore(overall_score=0.8, score_signature="SIG_1", explanation="Duplicate signature content", recommendation="GOOD_FOR_RETRIEVAL", quality_breakdown={"cohesion": 0.8})
    report_dup = ScoringValidator.validate([score1, score_dup])
    assert not report_dup.is_valid
    assert any("Duplicate signature detected" in e for e in report_dup.errors)

    # NaN / Range checks
    score_nan = ChunkScore(overall_score=float("nan"), score_signature="SIG_3", explanation="NaN content", recommendation="GOOD_FOR_RETRIEVAL", quality_breakdown={"cohesion": 0.5})
    report_nan = ScoringValidator.validate([score_nan])
    assert not report_nan.is_valid
    assert any("NaN value detected" in e for e in report_nan.errors)
