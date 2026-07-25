import logging
from typing import Dict, Any, Optional
from app.services.ai.config.provider_defaults import DEFAULT_PROVIDER_MODELS

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
        Eliminates hardcoded model strings from python source code.
        """
        p = provider_id.lower()
        cap_key = capability.lower() if capability else "default"

        # 1. Check custom overrides
        if p in cls._custom_mappings and cap_key in cls._custom_mappings[p]:
            return cls._custom_mappings[p][cap_key]

        # 2. Check default provider models
        prov_models = DEFAULT_PROVIDER_MODELS.get(p, {})
        if cap_key in prov_models:
            return prov_models[cap_key]

        return prov_models.get("default", "gpt-4o")

    @classmethod
    def get_all_mappings(cls) -> Dict[str, Any]:
        combined = {p: dict(models) for p, models in DEFAULT_PROVIDER_MODELS.items()}
        for p, overrides in cls._custom_mappings.items():
            if p not in combined:
                combined[p] = {}
            combined[p].update(overrides)
        return combined

    @classmethod
    def reset(cls) -> None:
        cls._custom_mappings.clear()
