import sys
import subprocess
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.ai.runtime import (
    RuntimeAnalytics,
    ProviderRecommendationEngine,
    RuntimeSandbox,
    RuntimeTimeline,
    TraceStore,
    RuntimeTrace
)
from app.services.ai.config import ProviderValidator
from app.services.ai.health.monitor import HealthMonitor

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_obs_plus_state():
    TraceStore.clear()
    RuntimeTimeline.reset()
    HealthMonitor.reset()
    yield
    TraceStore.clear()
    RuntimeTimeline.reset()
    HealthMonitor.reset()

def test_runtime_analytics_engine():
    t1 = RuntimeTrace(capability="chat", selected_provider="groq", selected_model="llama-3.3-70b-versatile", latency_ms=100.0, status="SUCCESS")
    t2 = RuntimeTrace(capability="reasoning", selected_provider="gemini", selected_model="gemini-2.5-flash", latency_ms=200.0, fallback_count=1, status="SUCCESS")
    TraceStore.add_trace(t1)
    TraceStore.add_trace(t2)

    analytics = RuntimeAnalytics.get_analytics_report()
    assert analytics["total_requests"] == 2
    assert analytics["average_latency_ms"] == 150.0
    assert analytics["success_rate_pct"] == 100.0
    assert "groq" in analytics["provider_usage_pct"]
    assert "gemini" in analytics["provider_usage_pct"]

def test_telemetry_provider_recommendation_engine():
    recs = ProviderRecommendationEngine.recommend_all()
    assert "chat" in recs
    assert "reasoning" in recs
    assert "recommended_provider" in recs["chat"]

def test_runtime_sandbox_simulation():
    res = RuntimeSandbox.simulate_failure(provider="groq", error_code=429, error_type="RateLimitError")
    assert res["simulation_success"] is True
    assert res["is_healthy"] is False

    # Clear simulation
    RuntimeSandbox.clear_simulation("groq")
    assert HealthMonitor.is_provider_healthy("groq") is True

def test_provider_validator():
    report = ProviderValidator.validate_all_providers()
    assert "system_valid" in report
    assert "total_scanned" in report
    assert report["total_scanned"] >= 5

def test_timeline_multi_format_exports():
    RuntimeTimeline.start(task_type="CHAT", capability="chat")
    RuntimeTimeline.add_step("Provider Selector", {"selected": "groq"})

    json_str = RuntimeTimeline.generate_json()
    assert "Gateway" in json_str

    md_str = RuntimeTimeline.generate_markdown()
    assert "# Request Execution Timeline" in md_str

    html_str = RuntimeTimeline.generate_html()
    assert "<html>" in html_str

    seq_str = RuntimeTimeline.generate_mermaid_sequence()
    assert "sequenceDiagram" in seq_str

    flow_str = RuntimeTimeline.generate_mermaid_flowchart()
    assert "graph TD" in flow_str

def test_expanded_system_dashboard_apis():
    res_rank = client.get("/api/v1/system/providers/ranking")
    assert res_rank.status_code == 200
    assert "rankings" in res_rank.json()

    res_recs = client.get("/api/v1/system/providers/recommendations")
    assert res_recs.status_code == 200
    assert "chat" in res_recs.json()

    res_ana = client.get("/api/v1/system/analytics")
    assert res_ana.status_code == 200
    assert "total_requests" in res_ana.json()

    res_models = client.get("/api/v1/system/analytics/models")
    assert res_models.status_code == 200
    assert "model_usage_pct" in res_models.json()

@pytest.fixture
def cli_env():
    import os
    env = dict(os.environ)
    backend_dir = os.path.abspath("backend")
    env["PYTHONPATH"] = backend_dir + os.pathsep + env.get("PYTHONPATH", "")
    return env

def test_ai_runtime_cli_script(cli_env):
    res = subprocess.run([sys.executable, "backend/scripts/ai_runtime.py", "ranking"], capture_output=True, text=True, env=cli_env)
    assert res.returncode == 0
    assert "recommended_provider" in res.stdout
