import os
import json
import logging
from typing import Dict, Optional
from app.services.ai.policy.policy_profile import PolicyProfile

logger = logging.getLogger(__name__)

class PolicyLoader:
    """
    Loads PolicyProfile instances from JSON configuration files inside config/profiles.
    """
    _profiles_dir = os.path.join(os.path.dirname(__file__), "..", "config", "profiles")

    @classmethod
    def load_policy(cls, policy_name: str) -> Optional[PolicyProfile]:
        name_clean = policy_name.lower().replace(".json", "")
        file_path = os.path.join(cls._profiles_dir, f"{name_clean}.json")
        if not os.path.exists(file_path):
            logger.warning(f"[PolicyLoader] Policy file not found: {file_path}")
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return PolicyProfile(**data)
        except Exception as e:
            logger.error(f"[PolicyLoader] Failed to load policy '{policy_name}': {str(e)}")
            return None

    @classmethod
    def list_available_policies(cls) -> Dict[str, str]:
        results: Dict[str, str] = {}
        if not os.path.exists(cls._profiles_dir):
            return results
        for fname in os.listdir(cls._profiles_dir):
            if fname.endswith(".json"):
                pname = fname[:-5]
                policy = cls.load_policy(pname)
                results[pname] = policy.description if policy else "Configuration profile"
        return results
