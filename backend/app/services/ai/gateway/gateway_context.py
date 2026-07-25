import time
import uuid
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.services.ai.task.task_type import TaskType
from app.services.ai.capability.types import AICapability, AIRole

class GatewayContext(BaseModel):
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: Optional[str] = None
    workspace_id: Optional[str] = None
    document_ids: List[str] = Field(default_factory=list)

    task_type: TaskType = TaskType.CHAT
    selected_role: AIRole = AIRole.CHAT_AI
    selected_capability: AICapability = AICapability.CHAT

    candidate_providers: List[Dict[str, str]] = Field(default_factory=list)
    selected_provider: Optional[str] = None
    selected_model: Optional[str] = None

    fallback_history: List[dict] = Field(default_factory=list)
    execution_trace: List[str] = Field(default_factory=list)

    start_time: float = Field(default_factory=time.time)
    latency_ms: float = 0.0
    retry_count: int = 0
    health_snapshot: Dict[str, Any] = Field(default_factory=dict)

    def log_step(self, step_description: str) -> None:
        elapsed = (time.time() - self.start_time) * 1000
        self.execution_trace.append(f"[{elapsed:.1f}ms] {step_description}")

    def finalize(self) -> None:
        self.latency_ms = (time.time() - self.start_time) * 1000
