from app.services.ai.registry.main import ProviderRegistry
from app.services.ai.models.routing import ProviderSelection
from app.services.ai.interfaces.provider import BaseLLMProvider

class LLMFactory:
    """
    Backward compatibility facade for LLMFactory.
    Forwards resolution to ProviderRegistry and ProviderRuntime.
    """
    @classmethod
    def get_provider(cls, selection: ProviderSelection) -> BaseLLMProvider:
        try:
            provider_cls = ProviderRegistry.get_provider_class(selection.provider)
            if provider_cls:
                return provider_cls(model=selection.model)
        except Exception:
            pass
        from app.services.ai.providers.openai_provider import OpenAIProvider
        return OpenAIProvider(model=selection.model)
