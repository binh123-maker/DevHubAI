import os
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class ProviderEnvLoader:
    """
    Sole environment variable reader for AI Provider credentials and base URLs.
    No other component or provider plugin should read `.env` or os.environ directly.
    """

    @classmethod
    def get_api_key(cls, provider_id: str) -> Optional[str]:
        p = provider_id.lower()
        val = None
        if p == "openai":
            val = os.getenv("OPENAI_API_KEY") or os.getenv("AI_API_KEY")
        elif p == "gemini":
            val = os.getenv("GEMINI_API_KEY") or os.getenv("AI_API_KEY")
        elif p == "groq":
            val = os.getenv("GROQ_API_KEY") or os.getenv("AI_API_KEY")
        elif p == "openrouter":
            val = os.getenv("OPENROUTER_API_KEY") or os.getenv("AI_API_KEY")
        elif p == "ollama":
            val = os.getenv("OLLAMA_API_KEY")
        else:
            val = os.getenv(f"{p.upper()}_API_KEY") or os.getenv("AI_API_KEY")
        return val.strip() if val and val.strip() else None

    @classmethod
    def get_base_url(cls, provider_id: str) -> Optional[str]:
        p = provider_id.lower()
        val = None
        if p == "openai":
            val = os.getenv("OPENAI_BASE_URL") or os.getenv("AI_BASE_URL") or None
        elif p == "gemini":
            val = os.getenv("GEMINI_BASE_URL") or None
        elif p == "groq":
            val = os.getenv("GROQ_BASE_URL") or "https://api.groq.com/openai/v1"
        elif p == "openrouter":
            val = os.getenv("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1"
        elif p == "ollama":
            val = os.getenv("OLLAMA_BASE_URL") or "http://localhost:11434"
        else:
            val = os.getenv(f"{p.upper()}_BASE_URL")
        return val.strip() if val and val.strip() else None

    @classmethod
    def get_model(cls, provider_id: str) -> Optional[str]:
        p = provider_id.lower()
        val = None
        if p == "openai":
            val = os.getenv("OPENAI_MODEL")
        elif p == "gemini":
            val = os.getenv("GEMINI_MODEL")
        elif p == "groq":
            val = os.getenv("GROQ_MODEL")
        elif p == "openrouter":
            val = os.getenv("OPENROUTER_MODEL")
        elif p == "ollama":
            val = os.getenv("OLLAMA_MODEL")
        elif p == "claude":
            val = os.getenv("CLAUDE_MODEL")
        elif p == "deepseek":
            val = os.getenv("DEEPSEEK_MODEL")
        elif p == "grok":
            val = os.getenv("GROK_MODEL")
        elif p == "mistral":
            val = os.getenv("MISTRAL_MODEL")
        else:
            val = os.getenv(f"{p.upper()}_MODEL")
        return val.strip() if val and val.strip() else None

    @classmethod
    def load_all_env_credentials(cls) -> Dict[str, Dict[str, Optional[str]]]:
        providers = ["openai", "gemini", "groq", "openrouter", "ollama"]
        return {
            p: {
                "api_key": cls.get_api_key(p),
                "base_url": cls.get_base_url(p),
                "model": cls.get_model(p)
            }
            for p in providers
        }
