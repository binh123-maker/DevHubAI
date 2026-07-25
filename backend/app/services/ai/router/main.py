from typing import Optional, List, Dict
from app.core.config import settings
from app.services.ai.models.routing import ProviderSelection

class AIRouter:
    """
    Backward compatibility facade for AIRouter.
    Forwards resolution to ProviderCapabilityMatrix and ProviderConfigCenter.
    """
    @classmethod
    def select_provider(cls, candidates: Optional[List[Dict[str, str]]] = None) -> ProviderSelection:
        from app.services.ai.config.provider_config import ProviderConfigCenter
        from app.services.ai.config.provider_capability_matrix import ProviderCapabilityMatrix
        from app.services.ai.health.monitor import HealthMonitor

        # If explicit ai_provider is configured in settings (e.g. in test mocks)
        if getattr(settings, "ai_provider", None) and settings.ai_provider not in ["openai", "gemini", "groq", "ollama", "openrouter"]:
            return ProviderSelection(
                provider=settings.ai_provider,
                model=settings.ai_model or "test-model",
                reason="ExplicitConfiguredProvider"
            )

        if candidates:
            for candidate in candidates:
                p = candidate["provider"]
                m = candidate["model"]
                if HealthMonitor.is_provider_healthy(p):
                    return ProviderSelection(provider=p, model=m, reason="CapabilityPriorityHealthy")

        chain = ProviderCapabilityMatrix.get_priority_chain("chat")
        for p in chain:
            if HealthMonitor.is_provider_healthy(p):
                m = ProviderConfigCenter.resolve_model(p, "chat")
                return ProviderSelection(provider=p, model=m, reason="ConfiguredHealthyProvider")

        m = ProviderConfigCenter.resolve_model("openai", "chat")
        return ProviderSelection(provider="openai", model=m, reason="FallbackDefault")
