from typing import List, Optional, Any, Dict

class ChunkReplayPlayer:
    def __init__(self, chunks: List[Any]):
        self.chunks = chunks
        self.current_index = 0
        self.playing = False

    def current(self) -> Optional[Any]:
        if not self.chunks or self.current_index < 0 or self.current_index >= len(self.chunks):
            return None
        return self.chunks[self.current_index]

    def next(self) -> Optional[Any]:
        if self.current_index < len(self.chunks) - 1:
            self.current_index += 1
            return self.current()
        return None

    def previous(self) -> Optional[Any]:
        if self.current_index > 0:
            self.current_index -= 1
            return self.current()
        return None

    def jump(self, index: int) -> Optional[Any]:
        if 0 <= index < len(self.chunks):
            self.current_index = index
            return self.current()
        return None

    def reset(self) -> None:
        self.current_index = 0

    def restart(self) -> None:
        self.current_index = 0

    def length(self) -> int:
        return len(self.chunks)

    # 10.3D extended controls
    def play(self) -> List[Any]:
        self.playing = True
        result = []
        self.restart()
        while self.current_index < len(self.chunks):
            result.append(self.current())
            self.current_index += 1
        self.playing = False
        return result

    def pause(self) -> None:
        self.playing = False

    def stop(self) -> None:
        self.playing = False
        self.restart()

    def timeline(self) -> List[Dict[str, Any]]:
        timeline_list = []
        for idx, c in enumerate(self.chunks):
            timeline_list.append({
                "step": idx,
                "chunk_signature": c.chunk_signature,
                "content_snippet": c.content[:30],
                "tokens": c.estimated_tokens
            })
        return timeline_list
