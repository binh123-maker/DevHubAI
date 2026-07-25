from enum import Enum

class TaskType(str, Enum):
    CHAT = "chat"
    RAG_SEARCH = "rag_search"
    SUMMARIZATION = "summarization"
    DOCUMENT_QA = "document_qa"
    CODE_GENERATION = "code_generation"
    CODE_EXPLANATION = "code_explanation"
    CODE_REVIEW = "code_review"
    REASONING = "reasoning"
    TITLE_GENERATION = "title_generation"
    KEYWORD_EXTRACTION = "keyword_extraction"
    TAG_GENERATION = "tag_generation"
    DOCUMENT_ANALYSIS = "document_analysis"
    EMBEDDING = "embedding"
    CLASSIFICATION = "classification"
    UNKNOWN = "unknown"
