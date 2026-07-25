from abc import ABC, abstractmethod
from typing import Generator, List
from app.services.ai.models.capabilities import ProviderCapabilities
from app.services.ai.models.prompt import ChatRequest
from app.services.ai.models.response import UnifiedResponse

class BaseLLMProvider(ABC):
    """
    Standard interface for all LLM provider plugins.
    Every AI provider (OpenAI, Ollama, Gemini, Groq, OpenRouter, etc.)
    must inherit from this base class and register with @ProviderRegistry.register("provider_name").
    """
    @property
    @abstractmethod
    def capabilities(self) -> ProviderCapabilities:
        """Returns the supported capabilities of the provider."""
        pass

    @abstractmethod
    def generate_response(self, request: ChatRequest) -> UnifiedResponse:
        """Synchronous response generation."""
        pass

    @abstractmethod
    def generate_stream(self, request: ChatRequest) -> Generator[UnifiedResponse, None, None]:
        """Streaming response generation."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Health check endpoint to verify connectivity."""
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """Lists available models for the provider."""
        pass
