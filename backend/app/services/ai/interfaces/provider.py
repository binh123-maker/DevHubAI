from abc import ABC, abstractmethod
from typing import Generator, List
from app.services.ai.models.capabilities import ProviderCapabilities
from app.services.ai.models.prompt import ChatRequest
from app.services.ai.models.response import UnifiedResponse
from app.services.ai.exceptions import AIError

class BaseLLMProvider(ABC):
    @property
    @abstractmethod
    def capabilities(self) -> ProviderCapabilities:
        """Return the capabilities of this provider."""
        pass

    @abstractmethod
    def generate_response(self, request: ChatRequest) -> UnifiedResponse:
        """Generate a single response for the request."""
        pass

    @abstractmethod
    def generate_stream(self, request: ChatRequest) -> Generator[UnifiedResponse, None, None]:
        """Generate a streaming response for the request."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Perform a health check on the provider."""
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """List all available models for this provider."""
        pass
