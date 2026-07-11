import pytest
from unittest.mock import MagicMock, patch
from app.services.ai.registry.main import ProviderRegistry
from app.services.ai.factory.main import LLMFactory
from app.services.ai.router.main import AIRouter
from app.services.ai.models import ProviderSelection, PromptPackage, ChatMessage, ChatRequest, UnifiedResponse, UsageInfo
from app.services.ai.interfaces.provider import BaseLLMProvider
from app.services.ai.prompt.builder import PromptBuilder
from app.services.ai.orchestrator.main import AIOrchestrator
from app.services.ai.exceptions import AuthenticationError, RateLimitError

@pytest.fixture(autouse=True)
def mock_settings():
    with patch("app.services.ai.router.main.settings") as mock_router_settings:
        mock_router_settings.ai_provider = "mock"
        mock_router_settings.ai_model = "mock-model"
        mock_router_settings.ai_api_key = "mock-key"
        mock_router_settings.ai_base_url = "http://mock-url"
        mock_router_settings.ai_timeout = 5.0
        mock_router_settings.ai_max_tokens = 100
        mock_router_settings.ai_temperature = 0.5
        mock_router_settings.gemini_model = "gemini-2.5-flash"
        mock_router_settings.gemini_api_key = "gemini-key"
        yield mock_router_settings

# Create a mock provider for testing
class MockProvider(BaseLLMProvider):
    def __init__(self, model: str) -> None:
        self.model = model

    @property
    def capabilities(self):
        return None

    def generate_response(self, request: ChatRequest) -> UnifiedResponse:
        if request.prompt_package.messages[-1].content == "fail_auth":
            raise AuthenticationError("Auth failed")
        elif request.prompt_package.messages[-1].content == "fail_rate":
            raise RateLimitError("Rate limit exceeded")
            
        return UnifiedResponse(
            content="Mock Response",
            provider="mock",
            model=self.model,
            usage=UsageInfo(input_tokens=10, output_tokens=10, total_tokens=20)
        )

    def generate_stream(self, request: ChatRequest):
        yield UnifiedResponse(content="Mock Stream", provider="mock", model=self.model)

    def health_check(self) -> bool:
        return True

    def list_models(self):
        return ["mock-model"]

# Register MockProvider
ProviderRegistry._registry["mock"] = MockProvider


def test_registry():
    assert "mock" in ProviderRegistry.list_registered_providers()
    assert ProviderRegistry.get_provider_class("mock") == MockProvider


def test_router():
    selection = AIRouter.select_provider()
    assert selection.provider == "mock"
    assert selection.model == "mock-model"


def test_factory():
    selection = ProviderSelection(provider="mock", model="test-model")
    provider = LLMFactory.get_provider(selection)
    assert isinstance(provider, MockProvider)
    assert provider.model == "test-model"


def test_prompt_builder():
    db_msg1 = MagicMock()
    db_msg1.role.value = "user"
    db_msg1.content = "Hello"
    
    db_msg2 = MagicMock()
    db_msg2.role.value = "assistant"
    db_msg2.content = "Hi there"

    pkg = PromptBuilder.build_prompt(
        user_message="Explain RAG",
        context_text="RAG is Retrieval-Augmented Generation",
        history_messages=[db_msg1, db_msg2],
        system_instruction="You are a tutor"
    )

    assert pkg.system_prompt == "You are a tutor"
    assert len(pkg.messages) == 3
    assert pkg.messages[0].role == "user"
    assert pkg.messages[0].content == "Hello"
    assert pkg.messages[1].role == "assistant"
    assert pkg.messages[1].content == "Hi there"
    assert "RAG is Retrieval-Augmented Generation" in pkg.messages[2].content
    assert "Explain RAG" in pkg.messages[2].content


def test_orchestrator_success():
    resp = AIOrchestrator.generate_response("hello")
    assert resp.content == "Mock Response"
    assert resp.provider == "mock"
    assert resp.model == "mock-model"
    assert resp.usage.total_tokens == 20


def test_orchestrator_auth_error():
    with pytest.raises(AuthenticationError):
        AIOrchestrator.generate_response("fail_auth")
