"""
Default configuration constants for AI Providers
"""

DEFAULT_PROVIDER_MODELS = {
    "openai": {
        "chat": "gpt-4o",
        "document_qa": "gpt-4o",
        "rag_search": "gpt-4o",
        "summarization": "gpt-4o-mini",
        "reasoning": "gpt-4o",
        "code_explanation": "gpt-4o",
        "code_generation": "gpt-4o",
        "embedding": "text-embedding-3-small",
        "default": "gpt-4o"
    },
    "gemini": {
        "chat": "gemini-2.5-flash",
        "document_qa": "gemini-2.5-flash",
        "document_analysis": "gemini-2.5-flash",
        "summarization": "gemini-2.5-flash",
        "reasoning": "gemini-2.5-flash",
        "default": "gemini-2.5-flash"
    },
    "groq": {
        "chat": "llama-3.3-70b-versatile",
        "summarization": "llama-3.3-70b-versatile",
        "reasoning": "llama-3.3-70b-versatile",
        "title_generation": "llama-3.1-8b-instant",
        "tag_generation": "llama-3.1-8b-instant",
        "default": "llama-3.3-70b-versatile"
    },
    "ollama": {
        "chat": "qwen2.5:7b",
        "document_qa": "qwen2.5:7b",
        "keyword_extraction": "qwen2.5:7b",
        "embedding": "nomic-embed-text",
        "default": "qwen2.5:7b"
    },
    "openrouter": {
        "chat": "meta-llama/llama-3.3-70b-instruct",
        "reasoning": "meta-llama/llama-3.3-70b-instruct",
        "default": "meta-llama/llama-3.3-70b-instruct"
    }
}

DEFAULT_TIMEOUTS = {
    "openai": 30.0,
    "gemini": 30.0,
    "groq": 20.0,
    "openrouter": 35.0,
    "ollama": 60.0
}

DEFAULT_RETRY_LIMITS = {
    "openai": 2,
    "gemini": 2,
    "groq": 2,
    "openrouter": 2,
    "ollama": 1
}
