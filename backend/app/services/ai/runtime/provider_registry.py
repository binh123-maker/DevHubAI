import logging
from typing import Dict, List, Optional, Type, Union
from app.services.ai.runtime.provider_profile import ProviderProfile
from app.services.ai.runtime.provider_capability import Capability
from app.services.ai.providers.base import BaseLLMProvider

logger = logging.getLogger(__name__)

class ProviderRegistry:
    """
    Dynamic Provider Registry.
    Centralized repository of all active ProviderProfiles and Provider Plugin classes.
    No hardcoded provider definitions inside registry; profiles are dynamically loaded
    via ProviderLoader.
    """
    _profiles: Dict[str, ProviderProfile] = {}
    _provider_classes: Dict[str, Type[BaseLLMProvider]] = {}
    _initialized: bool = False

    @classmethod
    def _ensure_initialized(cls) -> None:
        if not cls._initialized and not cls._profiles:
            cls._initialized = True
            try:
                from app.services.ai.providers.openai_provider import OpenAIProvider
                from app.services.ai.providers.gemini_provider import GeminiProvider
                from app.services.ai.providers.groq_provider import GroqProvider
                from app.services.ai.providers.openrouter_provider import OpenRouterProvider
                from app.services.ai.providers.ollama_provider import OllamaProvider

                cls._provider_classes["openai"] = OpenAIProvider
                cls._provider_classes["gemini"] = GeminiProvider
                cls._provider_classes["groq"] = GroqProvider
                cls._provider_classes["openrouter"] = OpenRouterProvider
                cls._provider_classes["ollama"] = OllamaProvider
            except Exception as e:
                logger.warning(f"[ProviderRegistry] Failed pre-registering provider classes: {e}")

            from app.services.ai.config.provider_loader import ProviderLoader
            ProviderLoader.load_default_profiles()

    @classmethod
    def register(cls, profile: ProviderProfile, provider_class: Optional[Type[BaseLLMProvider]] = None) -> None:
        key = profile.provider_id.lower()
        cls._profiles[key] = profile
        if provider_class:
            cls._provider_classes[key] = provider_class
        logger.info(f"[ProviderRegistry] Registered dynamic profile: '{profile.display_name}' ({key})")

    @classmethod
    def register_provider(cls, profile: ProviderProfile, provider_class: Optional[Type[BaseLLMProvider]] = None) -> None:
        cls.register(profile, provider_class)

    @classmethod
    def unregister(cls, provider_id: str) -> bool:
        key = provider_id.lower()
        removed = False
        if key in cls._profiles:
            del cls._profiles[key]
            removed = True
        if key in cls._provider_classes:
            del cls._provider_classes[key]
            removed = True
        if removed:
            logger.info(f"[ProviderRegistry] Unregistered provider profile: '{key}'")
        return removed

    @classmethod
    def get(cls, provider_id: str) -> Optional[ProviderProfile]:
        cls._ensure_initialized()
        return cls._profiles.get(provider_id.lower())

    @classmethod
    def get_profile(cls, provider_id: str) -> Optional[ProviderProfile]:
        return cls.get(provider_id)

    @classmethod
    def get_provider_class(cls, provider_id: str) -> Optional[Type[BaseLLMProvider]]:
        cls._ensure_initialized()
        return cls._provider_classes.get(provider_id.lower())

    @classmethod
    def get_all(cls) -> List[ProviderProfile]:
        cls._ensure_initialized()
        return list(cls._profiles.values())

    @classmethod
    def list_registered_profiles(cls) -> List[ProviderProfile]:
        return cls.get_all()

    @classmethod
    def enabled_profiles(cls) -> List[ProviderProfile]:
        cls._ensure_initialized()
        return [p for p in cls._profiles.values() if p.enabled]

    @classmethod
    def healthy_profiles(cls) -> List[ProviderProfile]:
        from app.services.ai.health.monitor import HealthMonitor
        healthy = []
        for p in cls.enabled_profiles():
            if p.health_status in ("ONLINE", "HEALTHY") and HealthMonitor.is_provider_healthy(p.provider_id):
                healthy.append(p)
        return healthy

    @classmethod
    def profiles_for_capability(cls, capability: Union[Capability, str]) -> List[ProviderProfile]:
        candidates = [
            p for p in cls.healthy_profiles()
            if p.supports_capability(capability)
        ]
        candidates.sort(key=lambda p: p.priority)
        return candidates

    @classmethod
    def initialize_default_profiles(cls) -> None:
        """Loads built-in default profiles via ProviderLoader."""
        if cls._profiles:
            return
        cls._initialized = True
        from app.services.ai.config.provider_loader import ProviderLoader
        ProviderLoader.load_default_profiles()

    @classmethod
    def reset(cls) -> None:
        cls._profiles.clear()
        cls._provider_classes.clear()
        cls._initialized = False
