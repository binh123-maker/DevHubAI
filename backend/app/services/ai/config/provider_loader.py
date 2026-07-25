import json
import os
import logging
from typing import Dict, Any
from app.services.ai.config.provider_capability_matrix import ProviderCapabilityMatrix
from app.services.ai.config.provider_model import ProviderModel

logger = logging.getLogger(__name__)

class ProviderLoader:
    @classmethod
    def load_config_dict(cls, config: Dict[str, Any]) -> None:
        """
        Loads overrides for priorities and model mappings from a dictionary.
        """
        # Load priority overrides
        priorities = config.get("capabilities") or config.get("priorities") or {}
        for cap, chain in priorities.items():
            if isinstance(chain, list):
                ProviderCapabilityMatrix.set_priority_chain(cap, chain)

        # Load model overrides
        models = config.get("models") or {}
        for provider_id, cap_models in models.items():
            if isinstance(cap_models, dict):
                for cap, model_name in cap_models.items():
                    ProviderModel.set_custom_mapping(provider_id, cap, model_name)

    @classmethod
    def load_from_json_file(cls, filepath: str) -> bool:
        if not os.path.exists(filepath):
            return False
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                cls.load_config_dict(data)
                logger.info(f"[ProviderLoader] Successfully loaded provider config from {filepath}")
                return True
        except Exception as e:
            logger.error(f"[ProviderLoader] Error loading config from {filepath}: {str(e)}")
            return False
