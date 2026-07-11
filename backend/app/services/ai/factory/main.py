from app.services.ai.models.routing import ProviderSelection
from app.services.ai.registry.main import ProviderRegistry
from app.services.ai.interfaces.provider import BaseLLMProvider
from app.services.ai.exceptions import ConfigurationError

class LLMFactory:
    @staticmethod
    def get_provider(selection: ProviderSelection) -> BaseLLMProvider:
        """
        Resolve and instantiate the provider adapter from registry
        based on ProviderSelection.
        """
        try:
            provider_class = ProviderRegistry.get_provider_class(selection.provider)
            return provider_class(model=selection.model)
        except KeyError:
            raise ConfigurationError(f"Unsupported AI provider: {selection.provider}")
