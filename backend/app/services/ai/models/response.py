from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ChatMessage(BaseModel):
    role: str  # 'system', 'user', 'assistant'
    content: str

class UsageInfo(BaseModel):
    input_tokens: Optional[int] = 0
    output_tokens: Optional[int] = 0
    total_tokens: Optional[int] = 0

class UnifiedResponse(BaseModel):
    content: str
    provider: str
    model: str
    finish_reason: Optional[str] = None
    latency_ms: Optional[float] = None
    usage: Optional[UsageInfo] = None
    metadata: Optional[Dict[str, Any]] = None
    raw_response: Optional[Any] = None
