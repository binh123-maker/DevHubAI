from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.services.ai.models.response import ChatMessage

class PromptPackage(BaseModel):
    system_prompt: Optional[str] = None
    messages: List[ChatMessage]
    context: Optional[str] = None
    citations: Optional[List[Any]] = None
    conversation: Optional[List[Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ChatRequest(BaseModel):
    prompt_package: PromptPackage
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False
