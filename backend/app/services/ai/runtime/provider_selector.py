import logging
from typing import List, Dict, Union, Any
from app.services.ai.runtime.provider_capability import Capability
from app.services.ai.runtime.provider_registry import ProviderRegistry
from app.services.ai.runtime.provider_alias import ProviderAlias
from app.services.ai.health.monitor import HealthMonitor

logger = logging.getLogger(__name__)

class ProviderSelector:
    """
    Dynamic Provider Selector Engine.
    Queries ProviderRegistry profiles, resolves aliases, applies group routing policies,
    filters unhealthy providers, and sorts candidate chains by dynamic runtime policy/scores.
    """
    _current_policy: str = "PRIORITY" # PRIORITY, BEST_HEALTH, LOWEST_LATENCY, BALANCED, CHEAPEST, FREE_ONLY
    _current_group_policy: str = "ALL" # ALL, PREFER_CLOUD, PREFER_LOCAL, CLOUD_ONLY, LOCAL_ONLY, HYBRID

    @classmethod
    def set_policy(cls, policy_mode: str) -> None:
        cls._current_policy = policy_mode.upper()
        logger.info(f"[ProviderSelector] Active Runtime Policy set to: '{cls._current_policy}'")

    @classmethod
    def get_policy(cls) -> str:
        return cls._current_policy

    @classmethod
    def set_group_policy(cls, group_policy: str) -> None:
        cls._current_group_policy = group_policy.upper()
        logger.info(f"[ProviderSelector] Active Group Policy set to: '{cls._current_group_policy}'")

    @classmethod
    def get_group_policy(cls) -> str:
        return cls._current_group_policy

    @classmethod
    def reset(cls) -> None:
        cls._current_policy = "PRIORITY"
        cls._current_group_policy = "ALL"

    @classmethod
    def select_candidate_chain(cls, capability: Union[Capability, str]) -> List[Dict[str, str]]:
        """
        Returns an ordered candidate chain of {'provider': str, 'model': str}
        resolving aliases, group policies, health filters, and dynamic runtime policies.
        """
        from app.services.ai.config.provider_capability_matrix import ProviderCapabilityMatrix
        from app.services.ai.config.provider_config import ProviderConfigCenter

        # 1. Resolve alias if input is string alias
        input_str = capability.value if hasattr(capability, "value") else str(capability)
        resolved_target = ProviderAlias.resolve_alias(input_str)

        # If resolved directly to a registered provider ID, prefer that provider first
        direct_provider_profile = ProviderRegistry.get(resolved_target)
        cap_val = input_str
        if direct_provider_profile:
            cap_val = "chat"

        # 2. Get registered candidate profiles supporting capability
        candidate_profiles = ProviderRegistry.profiles_for_capability(cap_val)

        # If priority chain overrides exist in matrix, align profiles to that order first
        override_chain = ProviderCapabilityMatrix.get_priority_chain(cap_val)
        if override_chain:
            override_map = {p.lower(): idx for idx, p in enumerate(override_chain)}
            candidate_profiles.sort(key=lambda p: override_map.get(p.provider_id.lower(), 999))

        # 3. Apply Group Policy filtering
        filtered_profiles = []
        for p in candidate_profiles:
            group = getattr(p, "group", "cloud").lower()
            if cls._current_group_policy == "CLOUD_ONLY" and group != "cloud":
                continue
            if cls._current_group_policy == "LOCAL_ONLY" and group != "local":
                continue
            if cls._current_policy == "FREE_ONLY" and not (p.free_tier or p.local):
                continue
            filtered_profiles.append(p)

        # Group policy re-sorting for PREFER_CLOUD / PREFER_LOCAL / HYBRID
        if cls._current_group_policy == "PREFER_CLOUD":
            filtered_profiles.sort(key=lambda p: (0 if p.group == "cloud" else 1, p.priority))
        elif cls._current_group_policy == "PREFER_LOCAL":
            filtered_profiles.sort(key=lambda p: (0 if p.group == "local" else 1, p.priority))

        # 4. Apply Dynamic Runtime Policy Sorting if not default PRIORITY
        if cls._current_policy in ("BEST_HEALTH", "LOWEST_LATENCY", "BALANCED", "CHEAPEST"):
            filtered_profiles.sort(
                key=lambda p: p.calculate_score(cls._current_policy),
                reverse=True
            )

        # If resolved directly to specific provider via alias, move it to front if healthy & enabled
        if direct_provider_profile and direct_provider_profile in filtered_profiles:
            filtered_profiles.remove(direct_provider_profile)
            filtered_profiles.insert(0, direct_provider_profile)

        # 5. Build candidate list with resolved models
        candidate_chain: List[Dict[str, str]] = []
        for p in filtered_profiles:
            if not HealthMonitor.is_provider_healthy(p.provider_id):
                continue
            model = ProviderConfigCenter.resolve_model(p.provider_id, cap_val)
            candidate_chain.append({
                "provider": p.provider_id,
                "model": model or p.default_model or "gpt-4o"
            })

        # Fallback safety if chain is empty
        if not candidate_chain:
            candidate_chain = [{"provider": "openai", "model": "gpt-4o"}]

        logger.debug(f"[ProviderSelector] Policy '{cls._current_policy}' resolved '{input_str}' -> {candidate_chain}")
        return candidate_chain
