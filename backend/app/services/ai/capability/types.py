from enum import Enum
from typing import Dict
from app.services.ai.task.task_type import TaskType

class AICapability(str, Enum):
    CHAT = "chat"
    DOC_QA = "doc_qa"
    SUMMARIZATION = "summarization"
    CITATION = "citation"
    FLASHCARD = "flashcard"
    QUIZ = "quiz"
    KEYWORD_EXTRACTION = "keyword_extraction"
    QUERY_REWRITE = "query_rewrite"
    TITLE_GENERATION = "title_generation"
    TAG_GENERATION = "tag_generation"
    METADATA_EXTRACTION = "metadata_extraction"
    SEMANTIC_CLASSIFICATION = "semantic_classification"
    CODE_EXPLANATION = "code_explanation"
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    REASONING = "reasoning"
    RAG = "rag"
    EMBEDDING = "embedding"

# Logical AI Role Enums
class AIRole(str, Enum):
    CHAT_AI = "Chat AI"
    REASONING_AI = "Reasoning AI"
    SEARCH_AI = "Search AI"
    SUMMARY_AI = "Summary AI"
    CODE_AI = "Code AI"
    DOCUMENT_AI = "Document AI"
    EMBEDDING_AI = "Embedding AI"

# TaskType -> AICapability & AIRole Mapping Matrix
TASK_TO_ROLE_CAPABILITY_MAP: Dict[TaskType, tuple[AIRole, AICapability]] = {
    TaskType.CHAT: (AIRole.CHAT_AI, AICapability.CHAT),
    TaskType.RAG_SEARCH: (AIRole.SEARCH_AI, AICapability.RAG),
    TaskType.SUMMARIZATION: (AIRole.SUMMARY_AI, AICapability.SUMMARIZATION),
    TaskType.DOCUMENT_QA: (AIRole.DOCUMENT_AI, AICapability.DOC_QA),
    TaskType.CODE_GENERATION: (AIRole.CODE_AI, AICapability.CODE_GENERATION),
    TaskType.CODE_EXPLANATION: (AIRole.CODE_AI, AICapability.CODE_EXPLANATION),
    TaskType.CODE_REVIEW: (AIRole.CODE_AI, AICapability.CODE_REVIEW),
    TaskType.REASONING: (AIRole.REASONING_AI, AICapability.REASONING),
    TaskType.TITLE_GENERATION: (AIRole.CHAT_AI, AICapability.TITLE_GENERATION),
    TaskType.KEYWORD_EXTRACTION: (AIRole.DOCUMENT_AI, AICapability.KEYWORD_EXTRACTION),
    TaskType.TAG_GENERATION: (AIRole.DOCUMENT_AI, AICapability.TAG_GENERATION),
    TaskType.DOCUMENT_ANALYSIS: (AIRole.DOCUMENT_AI, AICapability.METADATA_EXTRACTION),
    TaskType.EMBEDDING: (AIRole.EMBEDDING_AI, AICapability.EMBEDDING),
    TaskType.CLASSIFICATION: (AIRole.DOCUMENT_AI, AICapability.SEMANTIC_CLASSIFICATION),
    TaskType.UNKNOWN: (AIRole.CHAT_AI, AICapability.CHAT),
}
