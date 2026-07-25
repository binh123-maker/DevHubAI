import time
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class RuntimeEvent(BaseModel):
    event_type: str
    timestamp: float = Field(default_factory=time.time)
    details: Dict[str, Any] = Field(default_factory=dict)

class ProviderSelectedEvent(RuntimeEvent):
    event_type: str = "ProviderSelected"
    provider_name: str
    model: str
    capability: str

class ProviderStartedEvent(RuntimeEvent):
    event_type: str = "ProviderStarted"
    provider_name: str
    model: str

class ProviderFinishedEvent(RuntimeEvent):
    event_type: str = "ProviderFinished"
    provider_name: str
    model: str
    latency_ms: float
    tokens: int = 0

class ProviderFailedEvent(RuntimeEvent):
    event_type: str = "ProviderFailed"
    provider_name: str
    model: str
    error_type: str
    error_message: str

class ProviderSkippedEvent(RuntimeEvent):
    event_type: str = "ProviderSkipped"
    provider_name: str
    reason: str

class CapabilityResolvedEvent(RuntimeEvent):
    event_type: str = "CapabilityResolved"
    capability: str
    candidate_chain: list

class RuntimeCompletedEvent(RuntimeEvent):
    event_type: str = "RuntimeCompleted"
    selected_provider: str
    model: str
    total_latency_ms: float
    fallback_count: int = 0
