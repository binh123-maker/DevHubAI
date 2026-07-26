import logging
from typing import Dict, Type
from app.services.ai.interfaces.provider import BaseLLMProvider

logger = logging.getLogger(__name__)

class ProviderRegistry:
    _registry: Dict[str, Type[BaseLLMProvider]] = {}
    _initialized: bool = False

    @classmethod
    def _ensure_initialized(cls) -> None:
        if not cls._initialized:
            cls._initialized = True
            try:
                from app.services.ai.providers.openai_provider import OpenAIProvider
                from app.services.ai.providers.gemini_provider import GeminiProvider
                from app.services.ai.providers.groq_provider import GroqProvider
                from app.services.ai.providers.openrouter_provider import OpenRouterProvider
                from app.services.ai.providers.ollama_provider import OllamaProvider

                cls._registry["openai"] = OpenAIProvider
                cls._registry["gemini"] = GeminiProvider
                cls._registry["groq"] = GroqProvider
                cls._registry["openrouter"] = OpenRouterProvider
                cls._registry["ollama"] = OllamaProvider
            except Exception as e:
                logger.warning(f"[ProviderRegistry] Failed to pre-register default providers: {e}")

    @classmethod
    def register(cls, name: str):
        """Decorator to register an AI provider."""
        def decorator(subclass: Type[BaseLLMProvider]):
            name_lower = name.lower()
            cls._registry[name_lower] = subclass
            # Also register in runtime ProviderRegistry
            try:
                from app.services.ai.runtime.provider_registry import ProviderRegistry as RuntimeRegistry
                from app.services.ai.runtime.provider_profile import ProviderProfile
                from app.services.ai.runtime.provider_capability import Capability
                RuntimeRegistry.register_provider(
                    profile=ProviderProfile(
                        provider_id=name_lower,
                        display_name=name.capitalize(),
                        capabilities=[Capability.CHAT]
                    ),
                    provider_class=subclass
                )
            except Exception:
                pass
            logger.info(f"Registered AI provider: {name}")
            return subclass
        return decorator

    @classmethod
    def get_provider_class(cls, name: str) -> Type[BaseLLMProvider]:
        """Retrieve a registered provider class."""
        cls._ensure_initialized()
        name_lower = name.lower()
        if name_lower in cls._registry:
            return cls._registry[name_lower]
        try:
            from app.services.ai.runtime.provider_registry import ProviderRegistry as RuntimeRegistry
            cls_found = RuntimeRegistry.get_provider_class(name_lower)
            if cls_found:
                return cls_found
        except Exception:
            pass
        raise KeyError(f"Provider '{name}' is not registered.")

    @classmethod
    def list_registered_providers(cls) -> list[str]:
        """List all registered provider names."""
        cls._ensure_initialized()
        return list(cls._registry.keys())
