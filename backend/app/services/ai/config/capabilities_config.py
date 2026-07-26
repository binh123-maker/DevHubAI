"""
Capabilities Configuration Matrix
Maps each system capability to an ordered list of candidate providers and model names.
Model names are resolved dynamically via ProviderModel.resolve_model().
"""
from typing import Dict, List, Any
from app.services.ai.config.provider_model import ProviderModel

RAW_CAPABILITY_PROVIDER_CHAINS: Dict[str, List[str]] = {
    "chat": ["openai", "groq", "gemini", "openrouter", "ollama"],
    "doc_qa": ["openai", "groq", "gemini", "ollama"],
    "summarization": ["groq", "gemini", "openai"],
    "citation": ["openai", "groq"],
    "flashcard": ["groq", "openai"],
    "quiz": ["groq", "openai"],
    "keyword_extraction": ["ollama", "groq"],
    "query_rewrite": ["ollama", "groq"],
    "title_generation": ["groq", "ollama"],
    "tag_generation": ["groq", "ollama"],
    "metadata_extraction": ["ollama", "groq"],
    "semantic_classification": ["ollama", "groq"],
    "code_explanation": ["openai", "gemini", "groq"],
    "code_generation": ["openai", "gemini", "groq"],
    "code_review": ["openai", "gemini"],
    "reasoning": ["openai", "groq", "gemini", "openrouter", "ollama"],
    "rag": ["openai", "gemini", "openrouter", "groq"],
    "embedding": ["ollama", "openai"]
}

def get_capability_priorities() -> Dict[str, List[Dict[str, str]]]:
    result: Dict[str, List[Dict[str, str]]] = {}
    for cap, providers in RAW_CAPABILITY_PROVIDER_CHAINS.items():
        result[cap] = [
            {"provider": p, "model": ProviderModel.resolve_model(p, cap)}
            for p in providers
        ]
    return result

class DynamicCapabilityPriorities(dict):
    """
    Dynamic dictionary wrapper that resolves models at runtime via ProviderModel.resolve_model().
    """
    def __getitem__(self, key: Any) -> Any:
        priorities = get_capability_priorities()
        k = str(key).lower()
        if k in priorities:
            return priorities[k]
        return priorities.get("chat", [])

    def get(self, key: Any, default: Any = None) -> Any:
        priorities = get_capability_priorities()
        k = str(key).lower()
        if k in priorities:
            return priorities[k]
        return default if default is not None else priorities.get("chat", [])

    def items(self) -> Any:
        return get_capability_priorities().items()

    def values(self) -> Any:
        return get_capability_priorities().values()

    def keys(self) -> Any:
        return get_capability_priorities().keys()

    def __contains__(self, key: object) -> bool:
        return str(key).lower() in RAW_CAPABILITY_PROVIDER_CHAINS

DEFAULT_CAPABILITY_PRIORITIES = DynamicCapabilityPriorities()
