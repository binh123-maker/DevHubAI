import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ProviderModel:
    _custom_mappings: Dict[str, Dict[str, str]] = {}

    @classmethod
    def set_custom_mapping(cls, provider_id: str, capability: str, model_name: str) -> None:
        p = provider_id.lower()
        c = capability.lower()
        if p not in cls._custom_mappings:
            cls._custom_mappings[p] = {}
        cls._custom_mappings[p][c] = model_name
        logger.info(f"[ProviderModel] Configured custom model override: provider='{p}', capability='{c}' -> '{model_name}'")

    @classmethod
    def resolve_model(cls, provider_id: str, capability: Optional[str] = None) -> str:
        """
        Dynamically resolves the target model for a (provider, capability) pair.
        ProviderProfile is the authoritative source of truth.
        """
        details = cls.get_resolution_details(provider_id, capability)
        return details["resolved_model"]

    @classmethod
    def get_resolution_details(cls, provider_id: str, capability: Optional[str] = None) -> Dict[str, Any]:
        p = provider_id.lower()
        cap_key = capability.lower() if capability else None

        # 1. Custom mappings override
        if cap_key and p in cls._custom_mappings and cap_key in cls._custom_mappings[p]:
            return {
                "provider": p,
                "capability": cap_key,
                "resolved_model": cls._custom_mappings[p][cap_key],
                "model_source": "Capability Mapping",
                "override_applied": True
            }

        # 2. Check ProviderRegistry -> ProviderProfile
        from app.services.ai.runtime.provider_registry import ProviderRegistry
        from app.services.ai.config.provider_env_loader import ProviderEnvLoader

        profile = ProviderRegistry.get(p)
        if profile:
            if cap_key and profile.capability_models and cap_key in profile.capability_models:
                return {
                    "provider": p,
                    "capability": cap_key,
                    "resolved_model": profile.capability_models[cap_key],
                    "model_source": "Capability Mapping",
                    "override_applied": True
                }
            if profile.default_model:
                env_model = ProviderEnvLoader.get_model(p)
                model_source = "ENV" if (env_model and profile.default_model == env_model) else "ProviderProfile"
                return {
                    "provider": p,
                    "capability": cap_key or "default",
                    "resolved_model": profile.default_model,
                    "model_source": model_source,
                    "override_applied": bool(env_model)
                }

        # 3. Bootstrap fallback from provider_defaults template if profile not in registry yet
        from app.services.ai.config.provider_defaults import DEFAULT_PROVIDER_PROFILES
        template = DEFAULT_PROVIDER_PROFILES.get(p, {})
        default_mod = template.get("default_model", "gpt-4o")
        env_model = ProviderEnvLoader.get_model(p)
        final_model = env_model or default_mod
        return {
            "provider": p,
            "capability": cap_key or "default",
            "resolved_model": final_model,
            "model_source": "ENV" if env_model else "ProviderProfile",
            "override_applied": bool(env_model)
        }

    @classmethod
    def get_all_mappings(cls) -> Dict[str, Any]:
        from app.services.ai.runtime.provider_registry import ProviderRegistry
        from app.services.ai.config.provider_defaults import DEFAULT_PROVIDER_PROFILES

        result: Dict[str, Dict[str, str]] = {}
        for p_id in list(DEFAULT_PROVIDER_PROFILES.keys()):
            prof = ProviderRegistry.get(p_id)
            if prof:
                mapping = {"default": prof.default_model or "gpt-4o"}
                if prof.capability_models:
                    mapping.update(prof.capability_models)
                result[p_id] = mapping
            else:
                tmpl = DEFAULT_PROVIDER_PROFILES.get(p_id, {})
                result[p_id] = {"default": tmpl.get("default_model", "gpt-4o")}

        for p, overrides in cls._custom_mappings.items():
            if p not in result:
                result[p] = {}
            result[p].update(overrides)

        return result

    @classmethod
    def reset(cls) -> None:
        cls._custom_mappings.clear()
