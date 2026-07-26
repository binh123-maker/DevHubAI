import logging
from typing import Dict

logger = logging.getLogger(__name__)

class ProviderAlias:
    """
    Logical Alias Layer for AI Providers.
    Decouples business services from concrete provider names.
    Business services can request 'chat-ai', 'reasoning-ai', 'summary-ai', 'embedding-ai', etc.
    """
    _aliases: Dict[str, str] = {}

    @classmethod
    def register_alias(cls, alias: str, target: str) -> None:
        a_key = alias.lower()
        cls._aliases[a_key] = target.lower()
        logger.info(f"[ProviderAlias] Registered alias '{a_key}' -> '{target}'")

    @classmethod
    def update_alias(cls, alias: str, target: str) -> None:
        cls.register_alias(alias, target)

    @classmethod
    def resolve_alias(cls, alias: str) -> str:
        a_key = alias.lower()
        if a_key in cls._aliases:
            resolved = cls._aliases[a_key]
            logger.debug(f"[ProviderAlias] Resolved alias '{a_key}' -> '{resolved}'")
            return resolved
        return alias

    @classmethod
    def list_aliases(cls) -> Dict[str, str]:
        return dict(cls._aliases)

    @classmethod
    def initialize_defaults(cls) -> None:
        cls._aliases = {
            "chat-ai": "groq",
            "reasoning-ai": "groq",
            "summary-ai": "gemini",
            "embedding-ai": "ollama",
            "rag-ai": "openai",
            "document-ai": "gemini",
            "code-ai": "openai"
        }

    @classmethod
    def reset(cls) -> None:
        cls.initialize_defaults()

# Initialize defaults on load
ProviderAlias.initialize_defaults()
