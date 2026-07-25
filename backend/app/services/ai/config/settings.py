from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from app.core.config import settings as global_settings

class ProviderCredentials(BaseModel):
    provider_name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    default_model: str
    timeout: float = 30.0
    enabled: bool = True

class AIServiceSettings(BaseModel):
    default_provider: str = Field(default_factory=lambda: global_settings.ai_provider or "openai")
    default_model: str = Field(default_factory=lambda: global_settings.ai_model or "gpt-4o")
    openai_api_key: str = Field(default_factory=lambda: getattr(global_settings, "openai_api_key", global_settings.ai_api_key))
    openai_base_url: str = Field(default_factory=lambda: getattr(global_settings, "openai_base_url", global_settings.ai_base_url))
    groq_api_key: str = Field(default_factory=lambda: getattr(global_settings, "groq_api_key", ""))
    groq_base_url: str = Field(default_factory=lambda: getattr(global_settings, "groq_base_url", "https://api.groq.com/openai/v1"))
    openrouter_api_key: str = Field(default_factory=lambda: getattr(global_settings, "openrouter_api_key", ""))
    openrouter_base_url: str = Field(default_factory=lambda: getattr(global_settings, "openrouter_base_url", "https://openrouter.ai/api/v1"))
    gemini_api_key: str = Field(default_factory=lambda: getattr(global_settings, "gemini_api_key", global_settings.ai_api_key))
    ollama_base_url: str = Field(default_factory=lambda: getattr(global_settings, "ollama_base_url", "http://localhost:11434"))

    def get_provider_credentials(self, provider_name: str) -> ProviderCredentials:
        provider = provider_name.lower()
        if provider == "openai":
            return ProviderCredentials(
                provider_name="openai",
                api_key=self.openai_api_key or global_settings.ai_api_key,
                base_url=self.openai_base_url or global_settings.ai_base_url or None,
                default_model=global_settings.ai_model or "gpt-4o"
            )
        elif provider == "groq":
            return ProviderCredentials(
                provider_name="groq",
                api_key=self.groq_api_key or global_settings.ai_api_key,
                base_url=self.groq_base_url,
                default_model="llama-3.3-70b-versatile"
            )
        elif provider == "openrouter":
            return ProviderCredentials(
                provider_name="openrouter",
                api_key=self.openrouter_api_key or global_settings.ai_api_key,
                base_url=self.openrouter_base_url,
                default_model="meta-llama/llama-3.3-70b-instruct"
            )
        elif provider == "gemini":
            return ProviderCredentials(
                provider_name="gemini",
                api_key=self.gemini_api_key or global_settings.gemini_api_key or global_settings.ai_api_key,
                base_url=None,
                default_model=global_settings.gemini_model or "gemini-2.5-flash"
            )
        elif provider == "ollama":
            return ProviderCredentials(
                provider_name="ollama",
                api_key=None,
                base_url=self.ollama_base_url,
                default_model=getattr(global_settings, "ollama_model", "qwen2.5:7b")
            )
        return ProviderCredentials(
            provider_name=provider,
            api_key=global_settings.ai_api_key,
            base_url=global_settings.ai_base_url or None,
            default_model=global_settings.ai_model or "gpt-4o"
        )

ai_settings = AIServiceSettings()
