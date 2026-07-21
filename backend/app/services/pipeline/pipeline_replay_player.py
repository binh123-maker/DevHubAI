"""
Pipeline Replay Player — Phase 10.6

Step-through replay of a captured pipeline execution trace.
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ReplayFrame:
    index: int
    stage: str
    elapsed: float
    success: bool
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class PipelineReplayPlayer:
    """Replay pipeline executions frame by frame."""

    def __init__(self, execution_trace: List[Dict[str, Any]]) -> None:
        self._frames: List[ReplayFrame] = [
            ReplayFrame(
                index=i,
                stage=e.get("stage", ""),
                elapsed=e.get("elapsed", 0.0),
                success=e.get("success", True),
                timestamp=e.get("timestamp", 0.0),
                metadata=e.get("metadata", {}),
            )
            for i, e in enumerate(execution_trace)
        ]
        self._cursor: int = -1
        self._paused: bool = False

    # ------------------------------------------------------------------ controls
    def play(self) -> List[ReplayFrame]:
        """Return all frames from current cursor to end."""
        self._paused = False
        remaining = self._frames[self._cursor + 1 :]
        self._cursor = len(self._frames) - 1
        return remaining

    def pause(self) -> None:
        self._paused = True

    def resume(self) -> Optional[ReplayFrame]:
        self._paused = False
        return self.next()

    def next(self) -> Optional[ReplayFrame]:
        if self._paused:
            return None
        if self._cursor + 1 < len(self._frames):
            self._cursor += 1
            return self._frames[self._cursor]
        return None

    def previous(self) -> Optional[ReplayFrame]:
        if self._cursor > 0:
            self._cursor -= 1
            return self._frames[self._cursor]
        return None

    def jump(self, index: int) -> Optional[ReplayFrame]:
        if 0 <= index < len(self._frames):
            self._cursor = index
            return self._frames[self._cursor]
        return None

    def reset(self) -> None:
        self._cursor = -1
        self._paused = False

    # ------------------------------------------------------------------ filtering
    def filter_by_stage(self, stage_name: str) -> List[ReplayFrame]:
        return [f for f in self._frames if f.stage == stage_name]

    def filter_failures(self) -> List[ReplayFrame]:
        return [f for f in self._frames if not f.success]

    # ------------------------------------------------------------------ export
    def current_frame(self) -> Optional[ReplayFrame]:
        if 0 <= self._cursor < len(self._frames):
            return self._frames[self._cursor]
        return None

    def total_frames(self) -> int:
        return len(self._frames)

    def export_timeline(self) -> str:
        entries = []
        for f in self._frames:
            status = "✓" if f.success else "✗"
            entries.append(f"  [{f.index:02d}] {status} {f.stage:<35} {f.elapsed:.3f}s")
        return "\n".join(["Pipeline Replay Timeline", "-" * 60] + entries)

    def to_dict(self) -> List[Dict[str, Any]]:
        return [
            {
                "index": f.index,
                "stage": f.stage,
                "elapsed": f.elapsed,
                "success": f.success,
                "timestamp": f.timestamp,
            }
            for f in self._frames
        ]
