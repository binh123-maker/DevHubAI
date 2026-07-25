import logging
from typing import Dict, List, Optional, Type
from app.services.ai.runtime.provider_profile import ProviderProfile
from app.services.ai.runtime.provider_capability import Capability
from app.services.ai.providers.base import BaseLLMProvider

logger = logging.getLogger(__name__)

class ProviderRegistry:
    _profiles: Dict[str, ProviderProfile] = {}
    _provider_classes: Dict[str, Type[BaseLLMProvider]] = {}

    @classmethod
    def register_provider(cls, profile: ProviderProfile, provider_class: Optional[Type[BaseLLMProvider]] = None) -> None:
        key = profile.provider_id.lower()
        cls._profiles[key] = profile
        if provider_class:
            cls._provider_classes[key] = provider_class
        logger.info(f"[ProviderRegistry] Registered provider profile: '{profile.display_name}' ({key})")

    @classmethod
    def get_profile(cls, provider_id: str) -> Optional[ProviderProfile]:
        return cls._profiles.get(provider_id.lower())

    @classmethod
    def get_provider_class(cls, provider_id: str) -> Optional[Type[BaseLLMProvider]]:
        return cls._provider_classes.get(provider_id.lower())

    @classmethod
    def list_registered_profiles(cls) -> List[ProviderProfile]:
        return list(cls._profiles.values())

    @classmethod
    def initialize_default_profiles(cls) -> None:
        """Initializes default built-in profiles for standard providers."""
        if cls._profiles:
            return

        # 1. OpenAI Profile
        cls.register_provider(ProviderProfile(
            provider_id="openai",
            display_name="OpenAI",
            priority=10,
            supported_models=["gpt-4o", "gpt-4o-mini", "o3-mini"],
            capabilities=[Capability.CHAT, Capability.DOCUMENT_QA, Capability.RAG_SEARCH, Capability.CODE_GENERATION, Capability.CODE_EXPLANATION, Capability.CODE_REVIEW, Capability.REASONING, Capability.EMBEDDING],
            api_key_env="OPENAI_API_KEY",
            supports_reasoning=True,
            supports_multimodal=True,
            supports_embeddings=True,
            max_context=128000
        ))

        # 2. Gemini Profile
        cls.register_provider(ProviderProfile(
            provider_id="gemini",
            display_name="Google Gemini",
            priority=20,
            supported_models=["gemini-2.5-flash", "gemini-1.5-pro"],
            capabilities=[Capability.CHAT, Capability.DOCUMENT_QA, Capability.DOCUMENT_ANALYSIS, Capability.SUMMARIZATION, Capability.RAG_SEARCH, Capability.CODE_EXPLANATION, Capability.TRANSLATION],
            api_key_env="GEMINI_API_KEY",
            supports_multimodal=True,
            max_context=1000000
        ))

        # 3. Groq Profile
        cls.register_provider(ProviderProfile(
            provider_id="groq",
            display_name="Groq Cloud",
            priority=15,
            supported_models=["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
            capabilities=[Capability.CHAT, Capability.SUMMARIZATION, Capability.REASONING, Capability.TITLE_GENERATION, Capability.TAG_GENERATION, Capability.TRANSLATION, Capability.CODE_GENERATION],
            api_key_env="GROQ_API_KEY",
            supports_reasoning=True,
            max_context=128000
        ))

        # 4. Ollama Profile
        cls.register_provider(ProviderProfile(
            provider_id="ollama",
            display_name="Ollama Local",
            priority=30,
            supported_models=["qwen2.5:7b", "llama3.1:8b", "nomic-embed-text"],
            capabilities=[Capability.CHAT, Capability.DOCUMENT_QA, Capability.KEYWORD_EXTRACTION, Capability.TAG_GENERATION, Capability.CLASSIFICATION, Capability.EMBEDDING],
            api_key_env=None,
            base_url="http://localhost:11434",
            supports_embeddings=True,
            max_context=32768
        ))

        # 5. OpenRouter Profile
        cls.register_provider(ProviderProfile(
            provider_id="openrouter",
            display_name="OpenRouter Unified API",
            priority=25,
            supported_models=["meta-llama/llama-3.3-70b-instruct", "anthropic/claude-3.5-sonnet", "deepseek/deepseek-r1"],
            capabilities=[Capability.CHAT, Capability.DOCUMENT_QA, Capability.REASONING, Capability.RAG_SEARCH, Capability.SUMMARIZATION, Capability.CODE_GENERATION],
            api_key_env="OPENROUTER_API_KEY",
            supports_reasoning=True,
            max_context=200000
        ))

# Self-initialize defaults upon load
ProviderRegistry.initialize_default_profiles()
