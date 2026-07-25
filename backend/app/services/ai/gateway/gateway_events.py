import time
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class GatewayEvent(BaseModel):
    event_type: str
    trace_id: str
    timestamp: float = Field(default_factory=time.time)
    details: Dict[str, Any] = Field(default_factory=dict)

class FallbackEvent(GatewayEvent):
    event_type: str = "FALLBACK_TRIGGERED"
    failed_provider: str
    fallback_provider: str
    error_type: str
    error_message: str
