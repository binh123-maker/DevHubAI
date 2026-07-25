import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from app.services.ai.config.provider_env_loader import ProviderEnvLoader
from app.services.ai.config.provider_model import ProviderModel
from app.services.ai.config.provider_defaults import DEFAULT_TIMEOUTS

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
    Provider Configuration Center Facade.
    Single source of truth for all provider credentials, base URLs, model resolutions,
    timeouts, and priority matrices.
    No other component or provider plugin reads environment variables directly.
    """

    @classmethod
    def get_provider_config(cls, provider_id: str, capability: Optional[str] = None) -> ResolvedProviderConfig:
        p = provider_id.lower()
        api_key = ProviderEnvLoader.get_api_key(p)
        base_url = ProviderEnvLoader.get_base_url(p)
        model = ProviderModel.resolve_model(p, capability)
        timeout = DEFAULT_TIMEOUTS.get(p, 30.0)

        return ResolvedProviderConfig(
            provider_id=p,
            api_key=api_key,
            base_url=base_url,
            default_model=model,
            timeout=timeout,
            enabled=True
        )

    @classmethod
    def resolve_model(cls, provider_id: str, capability: Optional[str] = None) -> str:
        return ProviderModel.resolve_model(provider_id, capability)

    @classmethod
    def get_priority_chain(cls, capability: str) -> List[str]:
        from app.services.ai.config.provider_capability_matrix import ProviderCapabilityMatrix
        return ProviderCapabilityMatrix.get_priority_chain(capability)

    @classmethod
    def get_system_summary(cls) -> Dict[str, Any]:
        from app.services.ai.config.provider_capability_matrix import ProviderCapabilityMatrix
        return {
            "credentials": ProviderEnvLoader.load_all_env_credentials(),
            "models": ProviderModel.get_all_mappings(),
            "capability_matrix": ProviderCapabilityMatrix.get_matrix_snapshot()
        }
