import json
import os
import logging
from typing import Dict, Any, List, Optional
from app.services.ai.config.provider_defaults import DEFAULT_PROVIDER_PROFILES, DEFAULT_PROVIDER_MODELS
from app.services.ai.config.provider_env_loader import ProviderEnvLoader
from app.services.ai.runtime.provider_profile import ProviderProfile
from app.services.ai.runtime.provider_capability import Capability

logger = logging.getLogger(__name__)

class ProviderLoader:
    """
    Provider Loader Service.
    Automatically builds ProviderProfile objects from ProviderDefaults + .env + JSON/YAML configurations
    and registers them with ProviderRegistry.
    """

    @classmethod
    def create_profile(cls, provider_id: str, raw_data: Dict[str, Any]) -> ProviderProfile:
        p_id = provider_id.lower()
        data = dict(raw_data)
        data["provider_id"] = p_id

        # Merge environment credentials & URLs & models
        api_key = ProviderEnvLoader.get_api_key(p_id)
        base_url = ProviderEnvLoader.get_base_url(p_id)
        env_model = ProviderEnvLoader.get_model(p_id)
        if api_key and not data.get("api_key_name"):
            data["api_key_name"] = f"{p_id.upper()}_API_KEY"
        if base_url:
            data["base_url"] = base_url
        if env_model:
            data["default_model"] = env_model
            supp_models = list(data.get("supported_models", []))
            if env_model in supp_models:
                supp_models.remove(env_model)
            supp_models.insert(0, env_model)
            data["supported_models"] = supp_models

        # Parse capabilities strings to Capability Enum where possible
        raw_caps = data.get("capabilities", ["chat"])
        parsed_caps: List[Capability] = []
        for c in raw_caps:
            c_str = c.value if hasattr(c, "value") else str(c).lower()
            try:
                parsed_caps.append(Capability(c_str))
            except ValueError:
                pass
        data["capabilities"] = parsed_caps

        return ProviderProfile(**data)

    @classmethod
    def load_default_profiles(cls) -> List[ProviderProfile]:
        from app.services.ai.runtime.provider_registry import ProviderRegistry

        loaded: List[ProviderProfile] = []
        for p_id, template in DEFAULT_PROVIDER_PROFILES.items():
            profile = cls.create_profile(p_id, template)
            ProviderRegistry.register(profile)
            loaded.append(profile)

        logger.info(f"[ProviderLoader] Built and registered {len(loaded)} default ProviderProfiles.")
        return loaded

    @classmethod
    def load_from_dict(cls, config: Dict[str, Any]) -> List[ProviderProfile]:
        from app.services.ai.runtime.provider_registry import ProviderRegistry
        from app.services.ai.config.provider_capability_matrix import ProviderCapabilityMatrix
        from app.services.ai.config.provider_model import ProviderModel

        # 1. Load explicit profiles dictionary if present
        profiles_data = config.get("profiles") or config.get("providers") or {}
        loaded: List[ProviderProfile] = []

        if isinstance(profiles_data, dict):
            for p_id, p_data in profiles_data.items():
                if isinstance(p_data, dict):
                    base = dict(DEFAULT_PROVIDER_PROFILES.get(p_id.lower(), {}))
                    base.update(p_data)
                    profile = cls.create_profile(p_id, base)
                    ProviderRegistry.register(profile)
                    loaded.append(profile)

        elif isinstance(profiles_data, list):
            for p_data in profiles_data:
                if isinstance(p_data, dict) and "provider_id" in p_data:
                    p_id = p_data["provider_id"]
                    base = dict(DEFAULT_PROVIDER_PROFILES.get(p_id.lower(), {}))
                    base.update(p_data)
                    profile = cls.create_profile(p_id, base)
                    ProviderRegistry.register(profile)
                    loaded.append(profile)

        # 2. Load priority overrides
        priorities = config.get("capabilities") or config.get("priorities") or {}
        for cap, chain in priorities.items():
            if isinstance(chain, list):
                ProviderCapabilityMatrix.set_priority_chain(cap, chain)

        # 3. Load model overrides
        models = config.get("models") or {}
        for p_id, cap_models in models.items():
            if isinstance(cap_models, dict):
                for cap, model_name in cap_models.items():
                    ProviderModel.set_custom_mapping(p_id, cap, model_name)

        return loaded

    @classmethod
    def load_config_dict(cls, config: Dict[str, Any]) -> None:
        """Backward compatible helper function."""
        cls.load_from_dict(config)

    @classmethod
    def load_from_json_file(cls, filepath: str) -> bool:
        if not os.path.exists(filepath):
            return False
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                cls.load_from_dict(data)
                logger.info(f"[ProviderLoader] Successfully loaded provider config from {filepath}")
                return True
        except Exception as e:
            logger.error(f"[ProviderLoader] Error loading config from {filepath}: {str(e)}")
            return False

    @classmethod
    def load_from_yaml_file(cls, filepath: str) -> bool:
        if not os.path.exists(filepath):
            return False
        try:
            import yaml
            with open(filepath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                cls.load_from_dict(data)
                logger.info(f"[ProviderLoader] Successfully loaded YAML config from {filepath}")
                return True
        except Exception as e:
            logger.error(f"[ProviderLoader] Error loading YAML config from {filepath}: {str(e)}")
            return False

    @classmethod
    def load_and_register_all(cls) -> List[ProviderProfile]:
        cls.load_default_profiles()
        config_path = os.getenv("PROVIDER_CONFIG_PATH", "provider_config.json")
        if os.path.exists(config_path):
            cls.load_from_json_file(config_path)
        from app.services.ai.runtime.provider_registry import ProviderRegistry
        return ProviderRegistry.get_all()
