from enum import Enum
from typing import List, Dict

class Capability(str, Enum):
    CHAT = "chat"
    DOCUMENT_QA = "document_qa"
    DOCUMENT_ANALYSIS = "document_analysis"
    RAG_SEARCH = "rag_search"
    SUMMARIZATION = "summarization"
    TITLE_GENERATION = "title_generation"
    KEYWORD_EXTRACTION = "keyword_extraction"
    TAG_GENERATION = "tag_generation"
    CODE_GENERATION = "code_generation"
    CODE_EXPLANATION = "code_explanation"
    CODE_REVIEW = "code_review"
    REASONING = "reasoning"
    EMBEDDING = "embedding"
    CLASSIFICATION = "classification"
    TRANSLATION = "translation"
    UNKNOWN = "unknown"

# Default Capability Priority Mapping Matrix
DEFAULT_CAPABILITY_CHAINS: Dict[Capability, List[str]] = {
    Capability.CHAT: ["openai", "groq", "gemini", "openrouter", "ollama"],
    Capability.DOCUMENT_QA: ["gemini", "ollama", "groq", "openai", "openrouter"],
    Capability.DOCUMENT_ANALYSIS: ["gemini", "ollama", "groq", "openai"],
    Capability.RAG_SEARCH: ["openai", "gemini", "openrouter", "groq"],
    Capability.SUMMARIZATION: ["groq", "gemini", "openai", "openrouter"],
    Capability.TITLE_GENERATION: ["groq", "ollama", "openai"],
    Capability.KEYWORD_EXTRACTION: ["ollama", "groq", "openai"],
    Capability.TAG_GENERATION: ["groq", "ollama", "openai"],
    Capability.CODE_GENERATION: ["openai", "gemini", "groq", "openrouter"],
    Capability.CODE_EXPLANATION: ["openai", "gemini", "groq"],
    Capability.CODE_REVIEW: ["openai", "gemini", "groq"],
    Capability.REASONING: ["groq", "ollama", "gemini", "openai", "openrouter"],
    Capability.EMBEDDING: ["ollama", "openai"],
    Capability.CLASSIFICATION: ["ollama", "groq", "openai"],
    Capability.TRANSLATION: ["groq", "gemini", "openai"],
    Capability.UNKNOWN: ["openai", "groq", "gemini", "ollama"]
}
