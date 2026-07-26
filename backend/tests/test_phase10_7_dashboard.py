import pytest
from app.services.ai.runtime.runtime_dashboard import RuntimeDashboard
from app.services.ai.runtime.provider_registry import ProviderRegistry
from app.services.ai.policy import PolicyEngine

@pytest.fixture(autouse=True)
def reset_dashboard_state():
    PolicyEngine.reset()
    ProviderRegistry.reset()
    yield

def test_runtime_dashboard_snapshot():
    snapshot = RuntimeDashboard.get_snapshot()
    assert "timestamp" in snapshot
    assert "active_policy" in snapshot
    assert "providers" in snapshot
    assert snapshot["total_providers"] >= 5

    p_data = snapshot["providers"][0]
    assert "provider_id" in p_data
    assert "display_name" in p_data
    assert "health" in p_data
    assert "average_latency_ms" in p_data
    assert "average_tokens" in p_data
    assert "requests" in p_data
    assert "failures" in p_data
    assert "success_rate_pct" in p_data
