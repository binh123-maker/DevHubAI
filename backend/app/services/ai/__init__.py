# Import providers to ensure decorators execute and providers self-register
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
from app.services.ai.gateway.ai_gateway import AIGateway
from app.services.ai.task.task_analyzer import TaskAnalyzer
from app.services.ai.task.task_type import TaskType
from app.services.ai.capability.types import AICapability, AIRole
from app.services.ai.capability.router import CapabilityRouter
from app.services.ai.health.monitor import HealthMonitor
from app.services.ai.fallback.manager import FallbackManager
from app.services.ai.runtime import (
    Capability,
    ProviderProfile,
    ProviderSelector,
    ProviderResult,
    ProviderRuntime,
    ProviderStatistics,
    ProviderMetrics,
    ProviderManifest,
    ProviderExplanationReport,
    ProviderGraph
)

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
    "AIGateway",
    "TaskAnalyzer",
    "TaskType",
    "AICapability",
    "AIRole",
    "CapabilityRouter",
    "HealthMonitor",
    "FallbackManager",
    "Capability",
    "ProviderProfile",
    "ProviderSelector",
    "ProviderResult",
    "ProviderRuntime",
    "ProviderStatistics",
    "ProviderMetrics",
    "ProviderManifest",
    "ProviderExplanationReport",
    "ProviderGraph",
]
