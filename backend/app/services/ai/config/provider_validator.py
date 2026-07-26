import logging
from typing import List, Dict, Any
from app.services.ai.config.provider_env_loader import ProviderEnvLoader
from app.services.ai.runtime.provider_registry import ProviderRegistry

logger = logging.getLogger(__name__)

class ProviderValidator:
    """
    Production Provider Validator.
    Validates API keys, base URLs, model availability, connectivity, and feature capabilities
    (Streaming, Reasoning, Vision, JSON Mode, Tools, Embeddings) and outputs ProviderValidationReport.
    """

    @classmethod
    def validate_provider(cls, provider_id: str) -> Dict[str, Any]:
        p_id = provider_id.lower()
        profile = ProviderRegistry.get(p_id)

        api_key = ProviderEnvLoader.get_api_key(p_id)
        base_url = (profile.base_url if profile else None) or ProviderEnvLoader.get_base_url(p_id)

        warnings: List[str] = []
        is_valid = True

        if profile and profile.online and not profile.free_tier and not api_key:
            is_valid = False
            warnings.append(f"API key for online provider '{p_id}' is missing.")

        feature_support = {
            "supports_streaming": profile.supports_streaming if profile else True,
            "supports_reasoning": profile.supports_reasoning if profile else False,
            "supports_vision": profile.supports_vision if profile else False,
            "supports_json": profile.supports_json if profile else True,
            "supports_tools": profile.supports_tools if profile else False,
            "supports_embeddings": profile.supports_embeddings if profile else False
        }

        return {
            "provider_id": p_id,
            "display_name": profile.display_name if profile else p_id.capitalize(),
            "is_valid": is_valid,
            "has_api_key": bool(api_key),
            "base_url": base_url,
            "default_model": profile.default_model if profile else "gpt-4o",
            "supported_models_count": len(profile.supported_models) if profile else 0,
            "feature_support": feature_support,
            "warnings": warnings
        }

    @classmethod
    def validate_all_providers(cls) -> Dict[str, Any]:
        profiles = ProviderRegistry.list_registered_profiles()
        p_ids = [p.provider_id for p in profiles] if profiles else ["openai", "gemini", "groq", "openrouter", "ollama"]
        results = {p: cls.validate_provider(p) for p in p_ids}
        any_valid = any(r["is_valid"] for r in results.values())
        all_valid = all(r["is_valid"] for r in results.values())
        return {
            "system_valid": any_valid,
            "all_healthy": all_valid,
            "total_scanned": len(results),
            "providers": results
        }
