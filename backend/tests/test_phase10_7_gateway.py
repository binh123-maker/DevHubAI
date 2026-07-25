import pytest
from unittest.mock import MagicMock, patch
from app.services.ai import (
    AIGateway,
    TaskAnalyzer,
    TaskType,
    AICapability,
    AIRole,
    CapabilityRouter,
    HealthMonitor,
    FallbackManager,
    AIOrchestrator,
    UnifiedResponse,
    AuthenticationError,
    RateLimitError,
    TimeoutError
)
from app.services.ai.gateway import GatewayContext, GatewayMetrics
from app.services.ai.health.monitor import ProviderHealthStatus

@pytest.fixture(autouse=True)
def reset_monitors():
    HealthMonitor.reset()
    GatewayMetrics.reset()
    yield
    HealthMonitor.reset()
    GatewayMetrics.reset()

def test_task_analyzer_classification():
    # Test Chat
    t1, ctx1, c1 = TaskAnalyzer.analyze("Hello, how are you today?")
    assert t1 == TaskType.CHAT
    assert c1 >= 0.80

    # Test Summarization
    t2, ctx2, c2 = TaskAnalyzer.analyze("Please summarize the following document for me.")
    assert t2 == TaskType.SUMMARIZATION
    assert c2 >= 0.80

    # Test Code Explanation
    t3, ctx3, c3 = TaskAnalyzer.analyze("Explain this code:\n```python\ndef add(a, b):\n    return a + b\n```")
    assert t3 == TaskType.CODE_EXPLANATION
    assert c3 >= 0.80

    # Test Reasoning
    t4, ctx4, c4 = TaskAnalyzer.analyze("Solve this step-by-step math problem: 2x + 5 = 15")
    assert t4 == TaskType.REASONING

    # Test Document QA
    t5, ctx5, c5 = TaskAnalyzer.analyze("What is the author's argument?", context_text="Document excerpt text...")
    assert t5 == TaskType.DOCUMENT_QA

def test_capability_and_role_routing():
    role, cap = CapabilityRouter.resolve_role_and_capability(TaskType.REASONING)
    assert role == AIRole.REASONING_AI
    assert cap == AICapability.REASONING

    candidates = CapabilityRouter.get_candidate_providers(cap)
    assert len(candidates) > 0
    assert candidates[0]["provider"] == "openai"

def test_health_monitor_cooldown_lifecycle():
    assert HealthMonitor.is_provider_healthy("groq") is True

    # Record 429 rate limit error
    HealthMonitor.record_failure("groq", error_type="RateLimitError", status_code=429, cooldown_seconds=60.0)
    assert HealthMonitor.is_provider_healthy("groq") is False

    metrics = HealthMonitor.get_health_snapshot()["groq"]
    assert metrics["status"] == ProviderHealthStatus.COOLDOWN
    assert metrics["count_429"] == 1

def test_health_monitor_unauthorized():
    HealthMonitor.record_failure("openai", error_type="AuthenticationError", status_code=401)
    assert HealthMonitor.is_provider_healthy("openai") is False
    metrics = HealthMonitor.get_health_snapshot()["openai"]
    assert metrics["status"] == ProviderHealthStatus.UNAUTHORIZED

def test_fallback_manager_execution():
    candidate_chain = [
        {"provider": "failing_provider", "model": "m1"},
        {"provider": "healthy_provider", "model": "m2"}
    ]

    def mock_call(provider: str, model: str):
        if provider == "failing_provider":
            raise RateLimitError("Rate limit exceeded")
        return UnifiedResponse(content="Success response", provider=provider, model=model)

    res, history = FallbackManager.execute_with_fallback(candidate_chain, mock_call)
    assert res.content == "Success response"
    assert res.provider == "healthy_provider"
    assert len(history) == 2
    assert history[0]["status"] == "FAILED"
    assert history[1]["status"] == "SUCCESS"

@patch("app.services.ai.orchestrator.main.AIOrchestrator.generate_response")
def test_ai_gateway_chat_flow(mock_generate):
    mock_generate.return_value = UnifiedResponse(
        content="AI Gateway Response",
        provider="openai",
        model="gpt-4o"
    )

    res = AIGateway.chat(message="Tell me a joke")
    assert res.content == "AI Gateway Response"
    assert mock_generate.called

@patch("app.services.ai.orchestrator.main.AIOrchestrator.generate_response")
def test_ai_gateway_intent_methods(mock_generate):
    mock_generate.return_value = UnifiedResponse(
        content="Method Output",
        provider="groq",
        model="llama-3.3-70b-versatile"
    )

    res_reason = AIGateway.reason(problem_statement="Why is the sky blue?")
    assert res_reason.content == "Method Output"

    res_summary = AIGateway.summarize(text_content="Long text snippet...")
    assert res_summary.content == "Method Output"

    res_title = AIGateway.generate_title(conversation_history=[])
    assert res_title.content == "Method Output"

def test_backward_compatibility_orchestrator():
    # Verify AIOrchestrator still functions as direct fallback entry
    with patch("app.services.ai.factory.main.LLMFactory.get_provider") as mock_factory:
        mock_provider = MagicMock()
        mock_provider.generate_response.return_value = UnifiedResponse(
            content="Direct Orchestrator Output",
            provider="gemini",
            model="gemini-2.5-flash"
        )
        mock_factory.return_value = mock_provider

        res = AIOrchestrator.generate_response(user_message="Direct call")
        assert res.content == "Direct Orchestrator Output"
