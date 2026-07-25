import pytest
from unittest.mock import MagicMock, patch
from app.services.ai.runtime import (
    Capability,
    ProviderProfile,
    ProviderRegistry,
    ProviderSelector,
    ProviderResult,
    ProviderRuntime,
    ProviderStatistics,
    ProviderMetrics,
    ProviderManifest,
    ProviderExplanationReport,
    ProviderGraph
)
from app.services.ai.models.response import UnifiedResponse, UsageInfo
from app.services.ai.gateway import AIGateway
from app.services.ai.health.monitor import HealthMonitor

@pytest.fixture(autouse=True)
def reset_runtime_state():
    ProviderStatistics.reset()
    ProviderMetrics.reset()
    HealthMonitor.reset()
    yield
    ProviderStatistics.reset()
    ProviderMetrics.reset()
    HealthMonitor.reset()

def test_provider_registration_and_profiles():
    profile = ProviderProfile(
        provider_id="custom_provider",
        display_name="Custom Test Provider",
        priority=5,
        supported_models=["custom-v1"],
        capabilities=[Capability.CHAT, Capability.REASONING]
    )
    ProviderRegistry.register_provider(profile)

    fetched = ProviderRegistry.get_profile("custom_provider")
    assert fetched is not None
    assert fetched.display_name == "Custom Test Provider"
    assert fetched.supports_capability(Capability.REASONING) is True

def test_provider_capability_routing():
    chain_doc = ProviderSelector.select_candidate_chain(Capability.DOCUMENT_QA)
    assert len(chain_doc) > 0
    providers = [c["provider"] for c in chain_doc]
    assert "gemini" in providers or "openai" in providers

    chain_reasoning = ProviderSelector.select_candidate_chain(Capability.REASONING)
    assert len(chain_reasoning) > 0
    assert chain_reasoning[0]["provider"] == "groq"

def test_provider_result_unified_model():
    result = ProviderResult(
        provider_name="groq",
        model="llama-3.3-70b-versatile",
        capability=Capability.SUMMARIZATION,
        response="This is a summary text.",
        usage=UsageInfo(input_tokens=100, output_tokens=50, total_tokens=150),
        latency_ms=120.5
    )

    assert result.provider_name == "groq"
    assert result.capability == Capability.SUMMARIZATION
    assert result.usage.total_tokens == 150
    assert result.success is True

@patch("app.services.ai.orchestrator.main.AIOrchestrator.generate_response")
def test_provider_runtime_execution(mock_generate):
    mock_generate.return_value = UnifiedResponse(
        content="Runtime Response Content",
        provider="gemini",
        model="gemini-2.5-flash",
        usage=UsageInfo(input_tokens=20, output_tokens=30, total_tokens=50)
    )

    result = ProviderRuntime.execute(
        capability=Capability.DOCUMENT_QA,
        user_message="Summarize attached document"
    )

    assert isinstance(result, ProviderResult)
    assert result.provider_name == "gemini"
    assert result.response == "Runtime Response Content"

    # Verify statistics and metrics recorded
    stats = ProviderStatistics.get_summary()
    assert "gemini" in stats
    assert stats["gemini"]["total_requests"] == 1

    metrics = ProviderMetrics.get_metrics_report()
    assert metrics["total_executions"] == 1
    assert "gemini" in metrics["provider_counts"]

def test_reports_manifest_and_graph():
    manifest = ProviderManifest.get_manifest()
    assert manifest["version"] == "10.7.0"
    assert manifest["total_registered_providers"] >= 5

    report_md = ProviderExplanationReport.generate_markdown(
        capability="document_qa",
        selected_provider="gemini",
        selected_model="gemini-2.5-flash",
        candidate_chain=[{"provider": "gemini", "model": "gemini-2.5-flash"}],
        fallback_history=[{"provider": "gemini", "model": "gemini-2.5-flash", "status": "SUCCESS"}],
        latency_ms=85.0
    )
    assert "Provider Execution Report" in report_md
    assert "gemini" in report_md

    report_json = ProviderExplanationReport.generate_json(
        capability="document_qa",
        selected_provider="gemini",
        selected_model="gemini-2.5-flash",
        candidate_chain=[],
        fallback_history=[],
        latency_ms=85.0
    )
    assert "gemini" in report_json

    mermaid_graph = ProviderGraph.generate_mermaid()
    assert "graph TD" in mermaid_graph
    assert "Cap_document_qa" in mermaid_graph

@patch("app.services.ai.orchestrator.main.AIOrchestrator.generate_response")
def test_ai_gateway_runtime_integration(mock_generate):
    mock_generate.return_value = UnifiedResponse(
        content="Gateway via Runtime Response",
        provider="groq",
        model="llama-3.3-70b-versatile"
    )

    response = AIGateway.chat(message="Solve this math problem: 5 + 5")
    assert response.content == "Gateway via Runtime Response"
    assert response.provider == "groq"
