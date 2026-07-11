from app.core.config import settings
from app.services.ai.models.routing import ProviderSelection

class AIRouter:
    @classmethod
    def select_provider(cls) -> ProviderSelection:
        """
        Determines the active AI provider and model based on configuration.
        Future implementations can add cost, latency, or capability-aware routing.
        """
        provider = settings.ai_provider or "gemini"
        
        # Determine model with backward compatible fallback
        model = settings.ai_model
        if not model:
            if provider == "gemini":
                model = settings.gemini_model or "gemini-2.5-flash"
            elif provider == "ollama":
                model = getattr(settings, "ollama_model", "qwen2.5:7b")
            else:
                model = "gpt-4o"  # default openai fallback

        return ProviderSelection(
            provider=provider,
            model=model,
            reason="ConfiguredProvider"
        )
