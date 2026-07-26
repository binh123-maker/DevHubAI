import pytest
from unittest.mock import patch
from app.services.ai.runtime.provider_sandbox import ProviderSandbox
from app.services.ai.models.response import UnifiedResponse, UsageInfo

@patch("app.services.ai.orchestrator.main.AIOrchestrator.generate_response")
def test_provider_sandbox_run(mock_generate):
    mock_generate.return_value = UnifiedResponse(
        content="Sandbox Test Output",
        provider="groq",
        model="llama-3.3-70b-versatile",
        usage=UsageInfo(input_tokens=5, output_tokens=10, total_tokens=15)
    )

    res = ProviderSandbox.run(
        provider="groq",
        model="llama-3.3-70b-versatile",
        prompt="Explain RAG"
    )

    assert res["success"] is True
    assert res["provider"] == "groq"
    assert res["response"] == "Sandbox Test Output"
    assert res["latency_ms"] >= 0.0
