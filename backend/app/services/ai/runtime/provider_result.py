from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.services.ai.runtime.provider_capability import Capability
from app.services.ai.models.response import UsageInfo

class ProviderResult(BaseModel):
    provider_name: str
    model: str
    capability: Capability
    response: str
    reasoning: Optional[str] = None
    citations: List[dict] = Field(default_factory=list)
    usage: Optional[UsageInfo] = None
    latency_ms: float = 0.0
    finish_reason: str = "stop"
    success: bool = True
    error: Optional[str] = None
    retry_count: int = 0
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
