"""
Pipeline Events — Phase 10.6

Structured event classes emitted by every pipeline component.
"""
from __future__ import annotations
import time
import uuid
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class PipelineEvent:
    event_type: str
    pipeline_id: Optional[str] = None
    stage_name: Optional[str] = None
    details: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: uuid.uuid4().hex)


class PipelineStarted(PipelineEvent):
    def __init__(self, pipeline_id: str, stage_count: int):
        super().__init__("PipelineStarted", pipeline_id=pipeline_id, details=f"stages={stage_count}")


class PipelineFinished(PipelineEvent):
    def __init__(self, pipeline_id: str, health: float, elapsed: float):
        super().__init__("PipelineFinished", pipeline_id=pipeline_id,
                         details=f"health={health:.2f} elapsed={elapsed:.3f}s")


class StageStarted(PipelineEvent):
    def __init__(self, pipeline_id: str, stage_name: str):
        super().__init__("StageStarted", pipeline_id=pipeline_id, stage_name=stage_name)


class StageFinished(PipelineEvent):
    def __init__(self, pipeline_id: str, stage_name: str, elapsed: float, success: bool):
        super().__init__("StageFinished", pipeline_id=pipeline_id, stage_name=stage_name,
                         details=f"elapsed={elapsed:.3f}s success={success}")


class StageFailed(PipelineEvent):
    def __init__(self, pipeline_id: str, stage_name: str, error: str):
        super().__init__("StageFailed", pipeline_id=pipeline_id, stage_name=stage_name, details=error)


class RollbackStarted(PipelineEvent):
    def __init__(self, pipeline_id: str, stage_name: str):
        super().__init__("RollbackStarted", pipeline_id=pipeline_id, stage_name=stage_name)


class RollbackFinished(PipelineEvent):
    def __init__(self, pipeline_id: str, stage_name: str):
        super().__init__("RollbackFinished", pipeline_id=pipeline_id, stage_name=stage_name)


class FallbackActivated(PipelineEvent):
    def __init__(self, pipeline_id: str, reason: str):
        super().__init__("FallbackActivated", pipeline_id=pipeline_id, details=reason)


class PipelineRecovered(PipelineEvent):
    def __init__(self, pipeline_id: str, details: str = ""):
        super().__init__("PipelineRecovered", pipeline_id=pipeline_id, details=details)


class PipelineHealthy(PipelineEvent):
    def __init__(self, pipeline_id: str, health: float):
        super().__init__("PipelineHealthy", pipeline_id=pipeline_id, details=f"health={health:.2f}")


class StageRetrying(PipelineEvent):
    def __init__(self, pipeline_id: str, stage_name: str, attempt: int):
        super().__init__("StageRetrying", pipeline_id=pipeline_id, stage_name=stage_name,
                         details=f"attempt={attempt}")


class PluginLoaded(PipelineEvent):
    def __init__(self, pipeline_id: str, plugin_name: str):
        super().__init__("PluginLoaded", pipeline_id=pipeline_id, details=plugin_name)


class DependencyValidationFailed(PipelineEvent):
    def __init__(self, pipeline_id: str, reason: str):
        super().__init__("DependencyValidationFailed", pipeline_id=pipeline_id, details=reason)
