from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class TaskContext(BaseModel):
    message: str
    context_text: Optional[str] = None
    history_messages: Optional[List[Any]] = None
    has_documents: bool = False
    has_code_blocks: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)
