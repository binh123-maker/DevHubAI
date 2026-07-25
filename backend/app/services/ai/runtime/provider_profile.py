from typing import List, Optional
from pydantic import BaseModel, Field
from app.services.ai.runtime.provider_capability import Capability

class ProviderProfile(BaseModel):
    provider_id: str
    display_name: str
    version: str = "1.0.0"
    enabled: bool = True
    priority: int = 100
    supported_models: List[str] = Field(default_factory=list)
    capabilities: List[Capability] = Field(default_factory=list)
    base_url: Optional[str] = None
    api_key_env: Optional[str] = None

    supports_streaming: bool = True
    supports_json: bool = True
    supports_tools: bool = True
    supports_reasoning: bool = False
    supports_multimodal: bool = False
    supports_embeddings: bool = False

    max_context: int = 128000
    timeout: float = 30.0
    cooldown_seconds: float = 60.0
    retry_limit: int = 2
    health_score: float = 1.0

    def supports_capability(self, cap: Capability) -> bool:
        return cap in self.capabilities or Capability.CHAT in self.capabilities
