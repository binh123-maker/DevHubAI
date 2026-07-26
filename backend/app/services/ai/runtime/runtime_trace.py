import time
import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class RuntimeTrace(BaseModel):
    trace_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    start_time: float = Field(default_factory=time.time)
    finish_time: float = 0.0
    capability: str = "chat"
    task_type: str = "CHAT"
    selected_provider: str = ""
    selected_model: str = ""
    model_source: str = "ProviderProfile"
    override_applied: bool = False
    fallback_count: int = 0
    retry_count: int = 0
    latency_ms: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    reasoning_enabled: bool = False
    streaming_enabled: bool = False
    health_status: str = "ONLINE"
    finish_reason: str = "stop"
    status: str = "SUCCESS"

    def complete(
        self,
        selected_provider: str,
        selected_model: str,
        latency_ms: float,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        fallback_count: int = 0,
        retry_count: int = 0,
        reasoning_enabled: bool = False,
        streaming_enabled: bool = False,
        status: str = "SUCCESS",
        finish_reason: str = "stop",
        model_source: str = "ProviderProfile",
        override_applied: bool = False
    ) -> "RuntimeTrace":
        self.finish_time = time.time()
        self.selected_provider = selected_provider
        self.selected_model = selected_model
        self.model_source = model_source
        self.override_applied = override_applied
        self.latency_ms = latency_ms
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.fallback_count = fallback_count
        self.retry_count = retry_count
        self.reasoning_enabled = reasoning_enabled
        self.streaming_enabled = streaming_enabled
        self.status = status
        self.finish_reason = finish_reason
        return self

class TraceStore:
    """
    Thread-safe circular buffer storing recent RuntimeTraces.
    """
    _traces: List[RuntimeTrace] = []
    _max_traces: int = 500

    @classmethod
    def add_trace(cls, trace: RuntimeTrace) -> None:
        cls._traces.append(trace)
        if len(cls._traces) > cls._max_traces:
            cls._traces.pop(0)

    @classmethod
    def get_recent_traces(cls, limit: int = 50) -> List[Dict[str, Any]]:
        recent = cls._traces[-limit:] if limit > 0 else cls._traces
        return [t.model_dump() for t in reversed(recent)]

    @classmethod
    def get_trace(cls, trace_id: str) -> Optional[Dict[str, Any]]:
        for t in reversed(cls._traces):
            if t.trace_id == trace_id:
                return t.model_dump()
        return None

    @classmethod
    def get_all_raw(cls) -> List[RuntimeTrace]:
        return list(cls._traces)

    @classmethod
    def clear(cls) -> None:
        cls._traces.clear()
