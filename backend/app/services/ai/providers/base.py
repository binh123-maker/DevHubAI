from abc import ABC, abstractmethod
from typing import Generator, List, Optional, Any
from app.services.ai.models.capabilities import ProviderCapabilities
from app.services.ai.models.prompt import ChatRequest
from app.services.ai.models.response import UnifiedResponse

class BaseLLMProvider(ABC):
    """
    Standard interface for all LLM provider plugins.
    Every AI provider (OpenAI, Ollama, Gemini, Groq, OpenRouter, Claude, DeepSeek, etc.)
    inherits from this base class and registers with ProviderRegistry.
    """
    def initialize(self) -> None:
        """Initializes provider resources and clients."""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> ProviderCapabilities:
        """Returns the supported capabilities of the provider."""
        pass

    @abstractmethod
    def generate_response(self, request: ChatRequest) -> UnifiedResponse:
        """Synchronous response generation."""
        pass

    def generate(self, request: ChatRequest) -> UnifiedResponse:
        """Formalized alias for generate_response."""
        return self.generate_response(request)

    @abstractmethod
    def generate_stream(self, request: ChatRequest) -> Generator[UnifiedResponse, None, None]:
        """Streaming response generation."""
        pass

    def stream(self, request: ChatRequest) -> Generator[UnifiedResponse, None, None]:
        """Formalized alias for generate_stream."""
        return self.generate_stream(request)

    def embeddings(self, texts: List[str], model: Optional[str] = None) -> List[List[float]]:
        """Generates text embeddings if supported."""
        raise NotImplementedError(f"Provider '{self.__class__.__name__}' does not support embeddings.")

    @abstractmethod
    def health_check(self) -> bool:
        """Health check endpoint to verify connectivity."""
        pass

    def supports(self, capability: str) -> bool:
        """Checks whether this provider plugin supports the given capability string."""
        return True

    @abstractmethod
    def list_models(self) -> List[str]:
        """Lists available models for the provider."""
        pass

    def shutdown(self) -> None:
        """Cleans up provider resources upon shutdown."""
        pass
