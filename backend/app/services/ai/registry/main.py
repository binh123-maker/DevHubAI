import logging
from typing import Dict, Type
from app.services.ai.interfaces.provider import BaseLLMProvider

logger = logging.getLogger(__name__)

class ProviderRegistry:
    _registry: Dict[str, Type[BaseLLMProvider]] = {}

    @classmethod
    def register(cls, name: str):
        """Decorator to register an AI provider."""
        def decorator(subclass: Type[BaseLLMProvider]):
            cls._registry[name.lower()] = subclass
            logger.info(f"Registered AI provider: {name}")
            return subclass
        return decorator

    @classmethod
    def get_provider_class(cls, name: str) -> Type[BaseLLMProvider]:
        """Retrieve a registered provider class."""
        name_lower = name.lower()
        if name_lower not in cls._registry:
            raise KeyError(f"Provider '{name}' is not registered.")
        return cls._registry[name_lower]

    @classmethod
    def list_registered_providers(cls) -> list[str]:
        """List all registered provider names."""
        return list(cls._registry.keys())
