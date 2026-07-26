import logging
from typing import Dict, List, Optional, Any
from app.services.ai.policy.policy_profile import PolicyProfile
from app.services.ai.policy.policy_loader import PolicyLoader

logger = logging.getLogger(__name__)

class PolicyEngine:
    """
    Provider Policy Engine.
    Manages runtime policy profiles (development, production, low_cost, reasoning, coding).
    Dynamically applies priority chains, timeouts, retries, and preferred model mappings.
    """
    _current_policy_name: str = "production"
    _current_profile: Optional[PolicyProfile] = None

    @classmethod
    def set_policy(cls, policy_name: str) -> bool:
        profile = PolicyLoader.load_policy(policy_name)
        if not profile:
            logger.warning(f"[PolicyEngine] Unable to load policy profile '{policy_name}'. Retaining '{cls._current_policy_name}'.")
            return False

        cls._current_policy_name = profile.name.lower()
        cls._current_profile = profile

        # Apply priority chains to ProviderCapabilityMatrix
        from app.services.ai.config.provider_capability_matrix import ProviderCapabilityMatrix
        for cap, chain in profile.priorities.items():
            ProviderCapabilityMatrix.set_priority_chain(cap, chain)

        # Apply preferred model overrides
        from app.services.ai.config.provider_model import ProviderModel
        for p_id, cap_models in profile.preferred_models.items():
            for cap, mname in cap_models.items():
                ProviderModel.set_custom_mapping(p_id, cap, mname)

        logger.info(f"[PolicyEngine] Successfully switched active policy to: '{cls._current_policy_name}'")
        return True

    @classmethod
    def get_policy(cls) -> str:
        return cls._current_policy_name

    @classmethod
    def get_current_profile(cls) -> Optional[PolicyProfile]:
        if not cls._current_profile:
            cls.set_policy(cls._current_policy_name)
        return cls._current_profile

    @classmethod
    def get_priority_chain(cls, capability: str) -> List[str]:
        profile = cls.get_current_profile()
        c_key = capability.lower()
        if profile and c_key in profile.priorities:
            return profile.priorities[c_key]
        from app.services.ai.config.provider_capability_matrix import ProviderCapabilityMatrix
        return ProviderCapabilityMatrix.get_priority_chain(c_key)

    @classmethod
    def list_policies(cls) -> Dict[str, str]:
        return PolicyLoader.list_available_policies()

    @classmethod
    def reset(cls) -> None:
        cls._current_policy_name = "production"
        cls._current_profile = None
