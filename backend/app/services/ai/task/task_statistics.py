from typing import Dict
from app.services.ai.task.task_type import TaskType

class TaskStatistics:
    _counts: Dict[str, int] = {}

    @classmethod
    def record_task(cls, task_type: TaskType) -> None:
        key = task_type.value
        cls._counts[key] = cls._counts.get(key, 0) + 1

    @classmethod
    def get_statistics(cls) -> Dict[str, int]:
        return dict(cls._counts)

    @classmethod
    def reset(cls) -> None:
        cls._counts.clear()
