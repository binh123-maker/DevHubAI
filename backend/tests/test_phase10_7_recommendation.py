import pytest
from app.services.ai.runtime.recommendation_engine import RecommendationEngine
from app.services.ai.runtime.provider_registry import ProviderRegistry

@pytest.fixture(autouse=True)
def reset_rec_state():
    ProviderRegistry.reset()
    yield

def test_recommendation_engine_scoring():
    scores = RecommendationEngine.score_all_providers("chat")
    assert len(scores) > 0
    top = scores[0]
    assert "provider_id" in top
    assert "score" in top
    assert "metrics" in top
    assert top["score"] > 0

    best = RecommendationEngine.recommend_provider("chat")
    assert best is not None
    assert best["provider_id"] == top["provider_id"]
