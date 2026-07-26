import logging
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel
from app.services.ai.config.provider_env_loader import ProviderEnvLoader
from app.services.ai.config.provider_model import ProviderModel
from app.services.ai.config.provider_defaults import DEFAULT_TIMEOUTS
from app.services.ai.runtime.provider_profile import ProviderProfile
from app.services.ai.runtime.provider_registry import ProviderRegistry
from app.services.ai.runtime.provider_selector import ProviderSelector
from app.services.ai.runtime.provider_alias import ProviderAlias
from app.services.ai.health.monitor import HealthMonitor

logger = logging.getLogger(__name__)

class ResolvedProviderConfig(BaseModel):
    provider_id: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    default_model: str
    timeout: float = 30.0
    enabled: bool = True

class ProviderConfigCenter:
    """
    Provider Configuration Center Facade & Developer API.
    Single source of truth for all provider credentials, profiles, model resolutions,
    policies, aliases, enabling/disabling, pausing/resuming, and dynamic hot-reloading.
    """

    @classmethod
    def get_provider_config(cls, provider_id: str, capability: Optional[str] = None) -> ResolvedProviderConfig:
        p = provider_id.lower()
        profile = ProviderRegistry.get(p)

        api_key = ProviderEnvLoader.get_api_key(p)
        base_url = (profile.base_url if profile else None) or ProviderEnvLoader.get_base_url(p)
        model = ProviderModel.resolve_model(p, capability) or (profile.default_model if profile else "gpt-4o")
        timeout = (profile.timeout if profile else DEFAULT_TIMEOUTS.get(p, 30.0))
        enabled = (profile.enabled if profile else True)

        return ResolvedProviderConfig(
            provider_id=p,
            api_key=api_key,
            base_url=base_url,
            default_model=model,
            timeout=timeout,
            enabled=enabled
        )

    @classmethod
    def resolve_model(cls, provider_id: str, capability: Optional[str] = None) -> str:
        return ProviderModel.resolve_model(provider_id, capability)

    @classmethod
    def get_priority_chain(cls, capability: str) -> List[str]:
        from app.services.ai.config.provider_capability_matrix import ProviderCapabilityMatrix
        return ProviderCapabilityMatrix.get_priority_chain(capability)

    # --- Developer API Helper Methods ---

    @classmethod
    def list_profiles(cls) -> List[ProviderProfile]:
        return ProviderRegistry.get_all()

    @classmethod
    def get_profile(cls, provider: str) -> Optional[ProviderProfile]:
        return ProviderRegistry.get(provider)

    @classmethod
    def list_capabilities(cls) -> List[str]:
        from app.services.ai.runtime.provider_capability import Capability
        return [c.value for c in Capability]

    @classmethod
    def list_models(cls, provider: str) -> List[str]:
        profile = cls.get_profile(provider)
        if profile and profile.supported_models:
            return list(profile.supported_models)
        mappings = ProviderModel.get_all_mappings().get(provider.lower(), {})
        return list(set(mappings.values()))

    @classmethod
    def enable(cls, provider: str) -> None:
        profile = cls.get_profile(provider)
        if profile:
            profile.enabled = True
            HealthMonitor.resume(provider)
            logger.info(f"[ProviderConfigCenter] Enabled provider '{provider}'")

    @classmethod
    def disable(cls, provider: str) -> None:
        profile = cls.get_profile(provider)
        if profile:
            profile.enabled = False
            logger.info(f"[ProviderConfigCenter] Disabled provider '{provider}'")

    @classmethod
    def pause(cls, provider: str, duration_seconds: float = 60.0) -> None:
        HealthMonitor.pause(provider, duration_seconds)

    @classmethod
    def resume(cls, provider: str) -> None:
        HealthMonitor.resume(provider)

    @classmethod
    def set_policy(cls, policy_mode: str) -> None:
        ProviderSelector.set_policy(policy_mode)

    @classmethod
    def get_policy(cls) -> str:
        return ProviderSelector.get_policy()

    @classmethod
    def set_group_policy(cls, group_policy: str) -> None:
        ProviderSelector.set_group_policy(group_policy)

    @classmethod
    def get_group_policy(cls) -> str:
        return ProviderSelector.get_group_policy()

    @classmethod
    def update_priority(cls, target: str, priority_val: Any) -> None:
        t_lower = target.lower()
        profile = cls.get_profile(t_lower)
        if profile and isinstance(priority_val, int):
            profile.priority = priority_val
            logger.info(f"[ProviderConfigCenter] Updated profile priority for '{t_lower}' to {priority_val}")
        elif isinstance(priority_val, list):
            from app.services.ai.config.provider_capability_matrix import ProviderCapabilityMatrix
            ProviderCapabilityMatrix.set_priority_chain(t_lower, priority_val)
            logger.info(f"[ProviderConfigCenter] Updated priority chain for capability '{t_lower}' to {priority_val}")

    @classmethod
    def register_alias(cls, alias: str, provider: str) -> None:
        ProviderAlias.register_alias(alias, provider)

    @classmethod
    def resolve_alias(cls, alias: str) -> str:
        return ProviderAlias.resolve_alias(alias)

    # --- Dynamic Hot Reloading Methods ---

    @classmethod
    def reload(cls) -> None:
        from app.services.ai.config.provider_loader import ProviderLoader
        ProviderLoader.load_and_register_all()
        logger.info("[ProviderConfigCenter] Full system reload executed successfully.")

    @classmethod
    def reload_provider(cls, provider: str) -> None:
        cls.reload()

    @classmethod
    def reload_models(cls) -> None:
        ProviderModel.reset()
        cls.reload()

    @classmethod
    def reload_profiles(cls) -> None:
        ProviderRegistry.reset()
        cls.reload()

    @classmethod
    def get_system_summary(cls) -> Dict[str, Any]:
        from app.services.ai.config.provider_capability_matrix import ProviderCapabilityMatrix
        return {
            "credentials": ProviderEnvLoader.load_all_env_credentials(),
            "models": ProviderModel.get_all_mappings(),
            "capability_matrix": ProviderCapabilityMatrix.get_matrix_snapshot(),
            "profiles_count": len(ProviderRegistry.get_all()),
            "active_policy": cls.get_policy(),
            "active_group_policy": cls.get_group_policy()
        }
