from typing import List, Dict, Any, Optional

class ValidationReplayPlayer:
    def __init__(self, result: Any):
        self.result = result
        self.issues = result.issues
        self.current_index = 0
        self.playing = False
        self.play_speed = 1.0

    def current(self) -> Optional[Any]:
        if not self.issues or self.current_index < 0 or self.current_index >= len(self.issues):
            return None
        return self.issues[self.current_index]

    def next(self) -> Optional[Any]:
        if self.current_index < len(self.issues) - 1:
            self.current_index += 1
            return self.current()
        return None

    def previous(self) -> Optional[Any]:
        if self.current_index > 0:
            self.current_index -= 1
            return self.current()
        return None

    def jump(self, index: int) -> Optional[Any]:
        if 0 <= index < len(self.issues):
            self.current_index = index
            return self.current()
        return None

    def play(self) -> List[Any]:
        self.playing = True
        res = []
        self.current_index = 0
        while self.current_index < len(self.issues):
            res.append(self.current())
            self.current_index += 1
        self.playing = False
        return res

    def pause(self) -> None:
        self.playing = False

    def stop(self) -> None:
        self.playing = False
        self.current_index = 0

    def timeline(self) -> List[Dict[str, Any]]:
        timeline_list = []
        for idx, issue in enumerate(self.issues):
            timeline_list.append({
                "step": idx,
                "rule_name": issue.rule_name,
                "signature": issue.issue_signature,
                "severity": issue.severity
            })
        return timeline_list

    def export_timeline(self) -> List[Dict[str, Any]]:
        return self.timeline()

    def export_trace(self) -> List[Dict[str, Any]]:
        return self.result.validation_trace
