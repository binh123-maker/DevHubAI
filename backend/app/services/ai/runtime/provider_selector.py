import logging
from typing import List, Dict
from app.services.ai.runtime.provider_capability import Capability
from app.services.ai.runtime.provider_registry import ProviderRegistry

logger = logging.getLogger(__name__)

class ProviderSelector:
    @classmethod
    def select_candidate_chain(cls, capability: Capability) -> List[Dict[str, str]]:
        """
        Returns an ordered candidate chain of {'provider': str, 'model': str}
        for the given Capability, resolving priority chains and dynamic models via ProviderConfigCenter.
        """
        from app.services.ai.config.provider_capability_matrix import ProviderCapabilityMatrix
        from app.services.ai.config.provider_config import ProviderConfigCenter

        cap_val = capability.value if hasattr(capability, "value") else str(capability)
        chain_keys = ProviderCapabilityMatrix.get_priority_chain(cap_val)
        candidate_chain: List[Dict[str, str]] = []

        for p_key in chain_keys:
            profile = ProviderRegistry.get_profile(p_key)
            if profile and profile.enabled:
                model = ProviderConfigCenter.resolve_model(p_key, cap_val)
                candidate_chain.append({
                    "provider": profile.provider_id,
                    "model": model
                })

        logger.debug(f"[ProviderSelector] Resolved capability '{cap_val}' to candidate chain: {candidate_chain}")
        return candidate_chain
