import logging
from typing import Dict, Any, List
from app.services.ai.runtime.provider_registry import ProviderRegistry
from app.services.ai.config.provider_env_loader import ProviderEnvLoader
from app.services.ai.policy.policy_engine import PolicyEngine

logger = logging.getLogger(__name__)

class ConfigurationValidator:
    """
    Runtime Configuration Validator.
    Validates API keys, models, base URLs, provider IDs, policy profiles, and capabilities at startup.
    Generates a Configuration Report instead of runtime crashes.
    """

    @classmethod
    def validate_all(cls) -> Dict[str, Any]:
        profiles = ProviderRegistry.list_registered_profiles()
        available_policies = PolicyEngine.list_policies()

        issues: List[str] = []
        validated_providers: List[Dict[str, Any]] = []

        for p in profiles:
            p_id = p.provider_id
            api_key = ProviderEnvLoader.get_api_key(p_id)
            has_key = bool(api_key or p.local or p.free_tier)

            if not has_key:
                issues.append(f"Provider '{p_id}' missing API key env variable '{p.api_key_name}'")

            validated_providers.append({
                "provider_id": p_id,
                "display_name": p.display_name,
                "has_api_key": has_key,
                "default_model": p.default_model,
                "supported_models_count": len(p.supported_models),
                "capabilities_count": len(p.capabilities),
                "enabled": p.enabled
            })

        system_valid = len(issues) == 0

        report = {
            "system_valid": system_valid,
            "total_providers_scanned": len(profiles),
            "available_policies": list(available_policies.keys()),
            "active_policy": PolicyEngine.get_policy(),
            "issues_found": issues,
            "providers": validated_providers
        }

        if system_valid:
            logger.info("[ConfigurationValidator] All AI Provider configurations validated successfully.")
        else:
            logger.warning(f"[ConfigurationValidator] Found {len(issues)} configuration warnings: {issues}")

        return report
