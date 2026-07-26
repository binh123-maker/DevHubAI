import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.services.ai.runtime import (
    Capability,
    RuntimeTrace,
    TraceStore,
    RuntimeTimeline,
    ProviderDebugReport,
    RuntimeLogger,
    ProviderRuntime,
    ProviderResult
)
from app.services.ai.health.monitor import HealthMonitor, ProviderHealthStatus
from app.services.ai.models.response import UnifiedResponse, UsageInfo

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_obs_state():
    TraceStore.clear()
    RuntimeTimeline.reset()
    HealthMonitor.reset()
    yield
    TraceStore.clear()
    RuntimeTimeline.reset()
    HealthMonitor.reset()

def test_runtime_trace_and_store():
    trace = RuntimeTrace(capability="chat", task_type="CHAT")
    assert trace.trace_id is not None
    trace.complete(
        selected_provider="groq",
        selected_model="llama-3.3-70b-versatile",
        latency_ms=150.0,
        prompt_tokens=10,
        completion_tokens=20,
        status="SUCCESS"
    )
    TraceStore.add_trace(trace)

    recent = TraceStore.get_recent_traces(limit=10)
    assert len(recent) == 1
    assert recent[0]["trace_id"] == trace.trace_id
    assert recent[0]["selected_provider"] == "groq"
    assert recent[0]["latency_ms"] == 150.0

    fetched = TraceStore.get_trace(trace.trace_id)
    assert fetched is not None
    assert fetched["selected_model"] == "llama-3.3-70b-versatile"

def test_health_monitor_cooldown_remaining():
    HealthMonitor.record_failure("groq", error_type="RateLimitError", status_code=429, cooldown_seconds=60.0)
    snap = HealthMonitor.get_health_snapshot()
    assert "groq" in snap
    assert snap["groq"]["status"] in ("COOLDOWN", "RATE_LIMIT")

def test_provider_debug_report():
    report_json = ProviderDebugReport.generate_json()
    assert "analytics_summary" in report_json

    report_md = ProviderDebugReport.generate_markdown()
    assert "# AI Operations Center" in report_md

def test_system_dashboard_api_endpoints():
    res_providers = client.get("/api/v1/system/providers")
    assert res_providers.status_code == 200
    assert "providers" in res_providers.json()

    res_runtime = client.get("/api/v1/system/runtime")
    assert res_runtime.status_code == 200
    assert "active_policy" in res_runtime.json()

    res_traces = client.get("/api/v1/system/runtime/traces")
    assert res_traces.status_code == 200
    assert "recent_traces" in res_traces.json()

    res_metrics = client.get("/api/v1/system/runtime/metrics")
    assert res_metrics.status_code == 200
    assert "total_executions" in res_metrics.json()

@patch("app.services.ai.orchestrator.main.AIOrchestrator.generate_response")
def test_runtime_execution_with_trace_and_debug(mock_generate):
    mock_generate.return_value = UnifiedResponse(
        content="Observed Response",
        provider="openai",
        model="gpt-4o",
        usage=UsageInfo(input_tokens=15, output_tokens=25, total_tokens=40)
    )

    result = ProviderRuntime.execute(
        capability=Capability.CHAT,
        user_message="Hello observability"
    )

    assert isinstance(result, ProviderResult)
    assert result.provider_name == "openai"
    assert "trace_id" in result.metadata
    assert "runtime_info" in result.metadata
    assert result.metadata["runtime_info"]["selected_provider"] == "openai"
