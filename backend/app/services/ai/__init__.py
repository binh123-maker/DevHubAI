# Import providers to ensure they execute decorators and self-register
import app.services.ai.providers

from app.services.ai.exceptions import (
    AIError,
    AuthenticationError,
    ProviderUnavailableError,
    GenerationError,
    RateLimitError,
    TimeoutError,
    ConfigurationError
)
from app.services.ai.models import (
    ProviderCapabilities,
    ChatMessage,
    UsageInfo,
    UnifiedResponse,
    PromptPackage,
    ChatRequest,
    ProviderSelection
)
from app.services.ai.orchestrator.main import AIOrchestrator
from app.services.ai.prompt.builder import PromptBuilder
from app.services.ai.router.main import AIRouter
from app.services.ai.factory.main import LLMFactory
from app.services.ai.registry.main import ProviderRegistry

__all__ = [
    "AIError",
    "AuthenticationError",
    "ProviderUnavailableError",
    "GenerationError",
    "RateLimitError",
    "TimeoutError",
    "ConfigurationError",
    "ProviderCapabilities",
    "ChatMessage",
    "UsageInfo",
    "UnifiedResponse",
    "PromptPackage",
    "ChatRequest",
    "ProviderSelection",
    "AIOrchestrator",
    "PromptBuilder",
    "AIRouter",
    "LLMFactory",
    "ProviderRegistry",
]
