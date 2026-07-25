import re
from typing import Tuple
from app.services.ai.task.task_type import TaskType
from app.services.ai.task.task_context import TaskContext
from app.services.ai.task.task_rules import TASK_KEYWORD_RULES, check_code_presence

class TaskClassifier:
    @staticmethod
    def classify(context: TaskContext) -> Tuple[TaskType, float]:
        """
        Classifies task type using fast deterministic rules without LLM latency.
        Returns (TaskType, confidence_score).
        """
        message_lower = context.message.lower().strip()

        # 1. Document / Context presence heuristics
        if context.has_documents or (context.context_text and len(context.context_text.strip()) > 10):
            # Check if it's a summary request over document
            for task_type, patterns, conf in TASK_KEYWORD_RULES:
                if task_type == TaskType.SUMMARIZATION:
                    for pattern in patterns:
                        if re.search(pattern, message_lower):
                            return TaskType.SUMMARIZATION, conf
            # Check if asking RAG or Document QA
            if "?" in message_lower or any(qw in message_lower for qw in ["what", "who", "where", "when", "why", "how", "find"]):
                return TaskType.DOCUMENT_QA, 0.90
            return TaskType.RAG_SEARCH, 0.85

        # 2. Keyword & Regex Rule Matching
        for task_type, patterns, conf in TASK_KEYWORD_RULES:
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return task_type, conf

        # 3. Code Detection heuristics
        if context.has_code_blocks or check_code_presence(context.message):
            if any(w in message_lower for w in ["explain", "understand", "what does"]):
                return TaskType.CODE_EXPLANATION, 0.85
            elif any(w in message_lower for w in ["review", "fix", "optimiz", "refactor"]):
                return TaskType.CODE_REVIEW, 0.85
            return TaskType.CODE_GENERATION, 0.80

        # 4. Default Conversational Chat
        return TaskType.CHAT, 0.95
