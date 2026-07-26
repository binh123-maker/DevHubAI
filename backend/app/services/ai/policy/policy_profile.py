from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class PolicyProfile(BaseModel):
    name: str
    description: str = ""
    priorities: Dict[str, List[str]] = Field(default_factory=dict)
    timeouts: Dict[str, float] = Field(default_factory=dict)
    retries: Dict[str, int] = Field(default_factory=dict)
    cooldown: float = 60.0
    enabled_providers: List[str] = Field(default_factory=list)
    preferred_models: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
