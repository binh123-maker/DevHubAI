"""
Capabilities Configuration Matrix
Maps each system capability to an ordered list of candidate providers and model names.
"""

DEFAULT_CAPABILITY_PRIORITIES = {
    "chat": [
        {"provider": "openai", "model": "gpt-4o"},
        {"provider": "groq", "model": "llama-3.3-70b-versatile"},
        {"provider": "gemini", "model": "gemini-2.5-flash"},
        {"provider": "openrouter", "model": "meta-llama/llama-3.3-70b-instruct"},
        {"provider": "ollama", "model": "qwen2.5:7b"}
    ],
    "doc_qa": [
        {"provider": "openai", "model": "gpt-4o"},
        {"provider": "groq", "model": "llama-3.3-70b-versatile"},
        {"provider": "gemini", "model": "gemini-2.5-flash"},
        {"provider": "ollama", "model": "qwen2.5:7b"}
    ],
    "summarization": [
        {"provider": "groq", "model": "llama-3.3-70b-versatile"},
        {"provider": "gemini", "model": "gemini-2.5-flash"},
        {"provider": "openai", "model": "gpt-4o-mini"}
    ],
    "citation": [
        {"provider": "openai", "model": "gpt-4o-mini"},
        {"provider": "groq", "model": "llama-3.3-70b-versatile"}
    ],
    "flashcard": [
        {"provider": "groq", "model": "llama-3.3-70b-versatile"},
        {"provider": "openai", "model": "gpt-4o-mini"}
    ],
    "quiz": [
        {"provider": "groq", "model": "llama-3.3-70b-versatile"},
        {"provider": "openai", "model": "gpt-4o-mini"}
    ],
    "keyword_extraction": [
        {"provider": "ollama", "model": "qwen2.5:7b"},
        {"provider": "groq", "model": "llama-3.1-8b-instant"}
    ],
    "query_rewrite": [
        {"provider": "ollama", "model": "qwen2.5:7b"},
        {"provider": "groq", "model": "llama-3.1-8b-instant"}
    ],
    "title_generation": [
        {"provider": "groq", "model": "llama-3.1-8b-instant"},
        {"provider": "ollama", "model": "qwen2.5:7b"}
    ],
    "tag_generation": [
        {"provider": "groq", "model": "llama-3.1-8b-instant"},
        {"provider": "ollama", "model": "qwen2.5:7b"}
    ],
    "metadata_extraction": [
        {"provider": "ollama", "model": "qwen2.5:7b"},
        {"provider": "groq", "model": "llama-3.1-8b-instant"}
    ],
    "semantic_classification": [
        {"provider": "ollama", "model": "qwen2.5:7b"},
        {"provider": "groq", "model": "llama-3.1-8b-instant"}
    ],
    "code_explanation": [
        {"provider": "openai", "model": "gpt-4o"},
        {"provider": "gemini", "model": "gemini-2.5-flash"},
        {"provider": "groq", "model": "llama-3.3-70b-versatile"}
    ],
    "code_generation": [
        {"provider": "openai", "model": "gpt-4o"},
        {"provider": "gemini", "model": "gemini-2.5-flash"},
        {"provider": "groq", "model": "llama-3.3-70b-versatile"}
    ],
    "code_review": [
        {"provider": "openai", "model": "gpt-4o"},
        {"provider": "gemini", "model": "gemini-2.5-flash"}
    ],
    "reasoning": [
        {"provider": "openai", "model": "gpt-4o"},
        {"provider": "groq", "model": "llama-3.3-70b-versatile"},
        {"provider": "gemini", "model": "gemini-2.5-flash"},
        {"provider": "openrouter", "model": "meta-llama/llama-3.3-70b-instruct"},
        {"provider": "ollama", "model": "qwen2.5:7b"}
    ],
    "rag": [
        {"provider": "openai", "model": "gpt-4o"},
        {"provider": "gemini", "model": "gemini-2.5-flash"},
        {"provider": "openrouter", "model": "meta-llama/llama-3.3-70b-instruct"},
        {"provider": "groq", "model": "llama-3.3-70b-versatile"}
    ],
    "embedding": [
        {"provider": "ollama", "model": "nomic-embed-text"},
        {"provider": "openai", "model": "text-embedding-3-small"}
    ]
}
