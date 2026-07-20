from typing import List, Optional, Any

class BoundaryReplayPlayer:
    def __init__(self, boundaries: List[Any]):
        self.boundaries = boundaries
        self.current_index = 0

    def current(self) -> Optional[Any]:
        if not self.boundaries or self.current_index < 0 or self.current_index >= len(self.boundaries):
            return None
        return self.boundaries[self.current_index]

    def next(self) -> Optional[Any]:
        if self.current_index < len(self.boundaries) - 1:
            self.current_index += 1
            return self.current()
        return None

    def previous(self) -> Optional[Any]:
        if self.current_index > 0:
            self.current_index -= 1
            return self.current()
        return None

    def jump(self, index: int) -> Optional[Any]:
        if 0 <= index < len(self.boundaries):
            self.current_index = index
            return self.current()
        return None
