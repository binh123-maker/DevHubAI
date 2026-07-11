from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class ProviderSelection(BaseModel):
    provider: str
    model: str
    reason: str = "Configured"
    priority: int = 1
    metadata: Dict[str, Any] = Field(default_factory=dict)
