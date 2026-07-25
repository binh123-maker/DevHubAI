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
        if p == "openai":
            return os.getenv("OPENAI_API_KEY") or os.getenv("AI_API_KEY")
        elif p == "gemini":
            return os.getenv("GEMINI_API_KEY") or os.getenv("AI_API_KEY")
        elif p == "groq":
            return os.getenv("GROQ_API_KEY") or os.getenv("AI_API_KEY")
        elif p == "openrouter":
            return os.getenv("OPENROUTER_API_KEY") or os.getenv("AI_API_KEY")
        elif p == "ollama":
            return os.getenv("OLLAMA_API_KEY")
        return os.getenv(f"{p.upper()}_API_KEY") or os.getenv("AI_API_KEY")

    @classmethod
    def get_base_url(cls, provider_id: str) -> Optional[str]:
        p = provider_id.lower()
        if p == "openai":
            return os.getenv("OPENAI_BASE_URL") or os.getenv("AI_BASE_URL") or None
        elif p == "gemini":
            return os.getenv("GEMINI_BASE_URL") or None
        elif p == "groq":
            return os.getenv("GROQ_BASE_URL") or "https://api.groq.com/openai/v1"
        elif p == "openrouter":
            return os.getenv("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1"
        elif p == "ollama":
            return os.getenv("OLLAMA_BASE_URL") or "http://localhost:11434"
        return os.getenv(f"{p.upper()}_BASE_URL")

    @classmethod
    def load_all_env_credentials(cls) -> Dict[str, Dict[str, Optional[str]]]:
        providers = ["openai", "gemini", "groq", "openrouter", "ollama"]
        return {
            p: {
                "api_key": cls.get_api_key(p),
                "base_url": cls.get_base_url(p)
            }
            for p in providers
        }
