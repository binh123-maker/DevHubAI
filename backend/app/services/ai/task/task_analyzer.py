import logging
from typing import Optional, List, Any, Tuple
from app.services.ai.task.task_type import TaskType
from app.services.ai.task.task_context import TaskContext
from app.services.ai.task.task_classifier import TaskClassifier
from app.services.ai.task.task_statistics import TaskStatistics

logger = logging.getLogger(__name__)

class TaskAnalyzer:
    @classmethod
    def analyze(
        cls,
        message: str,
        context_text: Optional[str] = None,
        history_messages: Optional[List[Any]] = None,
        metadata: Optional[dict] = None
    ) -> Tuple[TaskType, TaskContext, float]:
        """
        Main entry point for task analysis.
        Inspects message, context, history, and metadata to return (TaskType, TaskContext, confidence).
        """
        metadata = metadata or {}
        has_docs = bool(metadata.get("document_ids") or (context_text and len(context_text.strip()) > 50))
        has_code = "```" in message or "def " in message or "function " in message

        task_context = TaskContext(
            message=message,
            context_text=context_text,
            history_messages=history_messages,
            has_documents=has_docs,
            has_code_blocks=has_code,
            metadata=metadata
        )

        task_type, confidence = TaskClassifier.classify(task_context)
        TaskStatistics.record_task(task_type)

        logger.info(f"[TaskAnalyzer] Classified message as TaskType.{task_type.name} (confidence={confidence:.2f})")
        return task_type, task_context, confidence
