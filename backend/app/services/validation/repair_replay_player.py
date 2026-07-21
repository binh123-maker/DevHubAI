from typing import List, Dict, Any, Optional

class RepairReplayPlayer:
    def __init__(self, result: Any):
        self.result = result
        self.issues = result.repaired_issues
        self.current_index = 0
        self.playing = False
        self.replay_speed = 1.0

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
                "repair_type": issue.repair_type,
                "signature": issue.repair_signature,
                "severity": issue.severity
            })
        return timeline_list

    def export_replay(self) -> List[Dict[str, Any]]:
        return self.timeline()
