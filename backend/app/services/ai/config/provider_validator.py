from typing import List, Dict, Any
from app.services.ai.config.provider_env_loader import ProviderEnvLoader

class ProviderValidator:
    @classmethod
    def validate_provider(cls, provider_id: str) -> Dict[str, Any]:
        p = provider_id.lower()
        api_key = ProviderEnvLoader.get_api_key(p)
        base_url = ProviderEnvLoader.get_base_url(p)

        warnings: List[str] = []
        is_valid = True

        if p in ["openai", "gemini", "groq", "openrouter"] and not api_key:
            is_valid = False
            warnings.append(f"API key for provider '{p}' is missing.")

        return {
            "provider_id": p,
            "is_valid": is_valid,
            "has_api_key": bool(api_key),
            "base_url": base_url,
            "warnings": warnings
        }

    @classmethod
    def validate_all_providers(cls) -> Dict[str, Any]:
        providers = ["openai", "gemini", "groq", "openrouter", "ollama"]
        results = {p: cls.validate_provider(p) for p in providers}
        all_valid = any(r["is_valid"] for r in results.values())
        return {
            "system_valid": all_valid,
            "providers": results
        }
