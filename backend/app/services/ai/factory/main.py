from app.services.ai.registry.main import ProviderRegistry
from app.services.ai.models.routing import ProviderSelection
from app.services.ai.interfaces.provider import BaseLLMProvider

class LLMFactory:
    """
    Factory for resolving LLM provider implementation instances.
    Maps provider IDs to their actual provider implementation classes.
    """

    @classmethod
    def get_provider(cls, selection: ProviderSelection) -> BaseLLMProvider:
        p_id = selection.provider.lower()

        if p_id == "gemini":
            from app.services.ai.providers.gemini_provider import GeminiProvider
            return GeminiProvider(model=selection.model)
        elif p_id == "openai":
            from app.services.ai.providers.openai_provider import OpenAIProvider
            return OpenAIProvider(model=selection.model)
        elif p_id == "groq":
            from app.services.ai.providers.groq_provider import GroqProvider
            return GroqProvider(model=selection.model)
        elif p_id == "openrouter":
            from app.services.ai.providers.openrouter_provider import OpenRouterProvider
            return OpenRouterProvider(model=selection.model)
        elif p_id == "ollama":
            from app.services.ai.providers.ollama_provider import OllamaProvider
            return OllamaProvider(model=selection.model)

        try:
            provider_cls = ProviderRegistry.get_provider_class(p_id)
            if provider_cls:
                return provider_cls(model=selection.model)
        except Exception:
            pass

        try:
            from app.services.ai.runtime.provider_registry import ProviderRegistry as RuntimeRegistry
            provider_cls = RuntimeRegistry.get_provider_class(p_id)
            if provider_cls:
                return provider_cls(model=selection.model)
        except Exception:
            pass

        from app.services.ai.providers.openai_provider import OpenAIProvider
        return OpenAIProvider(model=selection.model)
