from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, model_validator
from app.services.ai.runtime.provider_capability import Capability

class ProviderProfile(BaseModel):
    provider_id: str
    display_name: str
    description: str = ""
    priority: int = 100
    enabled: bool = True
    api_key_name: Optional[str] = None
    base_url: Optional[str] = None
    default_model: Optional[str] = None
    supported_models: List[str] = Field(default_factory=list)
    capability_models: Dict[str, str] = Field(default_factory=dict)
    capabilities: List[Capability] = Field(default_factory=list)

    supports_chat: bool = True
    supports_reasoning: bool = False
    supports_rag: bool = False
    supports_embeddings: bool = False
    supports_streaming: bool = True
    supports_tools: bool = False
    supports_json: bool = True
    supports_vision: bool = False
    supports_images: bool = False
    supports_audio: bool = False
    supports_multimodal: bool = False
    supports_function_calling: bool = False

    max_context_tokens: int = 128000
    max_output_tokens: int = 4096
    timeout: float = 30.0
    cooldown: float = 60.0
    retry_limit: int = 2

    cost_level: str = "medium"
    speed_level: str = "fast"
    quality_level: str = "high"
    free_tier: bool = False
    online: bool = True
    local: bool = False
    health_status: str = "ONLINE"
    health_score: float = 1.0

    group: str = "cloud"
    website_url: Optional[str] = None
    doc_url: Optional[str] = None
    api_version: str = "v1"
    provider_version: str = "1.0.0"
    supported_features: List[str] = Field(default_factory=list)
    release_date: Optional[str] = None
    maintainer: Optional[str] = None
    plugin_version: str = "1.0.0"

    metadata: Dict[str, Any] = Field(default_factory=dict)
    statistics: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def handle_legacy_aliases(cls, values: Any) -> Any:
        if isinstance(values, dict):
            if "api_key_env" in values and not values.get("api_key_name"):
                values["api_key_name"] = values["api_key_env"]
            if "max_context" in values and not values.get("max_context_tokens"):
                values["max_context_tokens"] = values["max_context"]
            if "cooldown_seconds" in values and not values.get("cooldown"):
                values["cooldown"] = values["cooldown_seconds"]
            if "version" in values and not values.get("provider_version"):
                values["provider_version"] = values["version"]
        return values

    @property
    def api_key_env(self) -> Optional[str]:
        return self.api_key_name

    @api_key_env.setter
    def api_key_env(self, value: Optional[str]) -> None:
        self.api_key_name = value

    @property
    def max_context(self) -> int:
        return self.max_context_tokens

    @max_context.setter
    def max_context(self, value: int) -> None:
        self.max_context_tokens = value

    @property
    def cooldown_seconds(self) -> float:
        return self.cooldown

    @cooldown_seconds.setter
    def cooldown_seconds(self, value: float) -> None:
        self.cooldown = value

    @property
    def version(self) -> str:
        return self.provider_version

    @version.setter
    def version(self, value: str) -> None:
        self.provider_version = value

    def supports_capability(self, cap: Union[Capability, str]) -> bool:
        cap_val = cap.value if hasattr(cap, "value") else str(cap).lower()
        cap_enum = None
        try:
            cap_enum = Capability(cap_val)
        except ValueError:
            pass

        if cap_enum and cap_enum in self.capabilities:
            return True

        if any((c.value if hasattr(c, "value") else str(c).lower()) == cap_val for c in self.capabilities):
            return True

        if cap_val in ("chat", "doc_qa", "summarization", "citation", "flashcard", "quiz") and self.supports_chat:
            return True
        if cap_val == "reasoning" and self.supports_reasoning:
            return True
        if cap_val in ("rag", "rag_search") and self.supports_rag:
            return True
        if cap_val == "embedding" and self.supports_embeddings:
            return True

        return False

    def calculate_score(self, policy_mode: str = "BALANCED") -> float:
        mode = policy_mode.upper()
        avg_lat = self.statistics.get("average_latency", 100.0)
        succ_rate = 1.0
        tot_req = self.statistics.get("total_requests", 0)
        if tot_req > 0:
            succ_rate = self.statistics.get("successful_requests", 0) / tot_req

        if mode == "PRIORITY":
            return float(1000 - self.priority)
        elif mode == "BEST_HEALTH":
            return self.health_score * 100.0
        elif mode == "LOWEST_LATENCY":
            return max(0.0, 5000.0 - avg_lat)
        elif mode == "CHEAPEST":
            cost_bonus = 50.0 if self.free_tier or self.local else (30.0 if self.cost_level == "low" else 10.0)
            return cost_bonus + (self.health_score * 50.0)
        else:
            priority_part = max(0, 100 - self.priority) * 0.20
            health_part = self.health_score * 35.0
            latency_part = max(0.0, (2000.0 - min(2000.0, avg_lat)) / 2000.0) * 25.0
            success_part = succ_rate * 20.0
            return priority_part + health_part + latency_part + success_part

