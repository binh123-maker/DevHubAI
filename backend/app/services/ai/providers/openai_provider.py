import logging
from typing import Generator, List, Any
import openai
from app.core.config import settings
from app.services.ai.registry.main import ProviderRegistry
from app.services.ai.interfaces.provider import BaseLLMProvider
from app.services.ai.models.capabilities import ProviderCapabilities
from app.services.ai.models.prompt import ChatRequest
from app.services.ai.models.response import UnifiedResponse, UsageInfo
from app.services.ai.exceptions import (
    AIError,
    AuthenticationError,
    ProviderUnavailableError,
    GenerationError,
    RateLimitError,
    TimeoutError,
    ConfigurationError
)

"""
This provider serves OpenAI and all OpenAI-compatible API endpoints.
Because services like Groq, OpenRouter, DeepSeek API, LM Studio, Together AI, 
Azure OpenAI, and other compatible platforms follow the standard OpenAI chat completions API,
they can all be configured dynamically using this single provider class by changing only:
- AI_PROVIDER (set to 'openai')
- AI_BASE_URL (pointing to the provider's endpoint)
- AI_API_KEY (providing the relevant API credential)
- AI_MODEL (specifying the target model name)

This design complies with the Open-Closed Principle (OCP) by avoiding separate provider
source files (e.g. GroqProvider or OpenRouterProvider) for compatible APIs.
"""

logger = logging.getLogger(__name__)

@ProviderRegistry.register("openai")
class OpenAIProvider(BaseLLMProvider):
    def __init__(self, model: str) -> None:
        self.model_name = model or settings.ai_model
        self.api_key = settings.ai_api_key
        self.base_url = settings.ai_base_url
        
        # Validate required configurations
        if not self.model_name:
            raise ConfigurationError("AI_MODEL must be configured for the OpenAI-compatible provider.")
            
        # Standard OpenAI API defaults to its official endpoint when base_url is empty.
        # Other compatible providers (Groq, OpenRouter, etc.) require base_url and api_key.
        if not self.api_key:
            # Local endpoints (LM Studio, local Ollama, etc.) might bypass api_key
            is_local = self.base_url and any(loc in self.base_url for loc in ["localhost", "127.0.0.1", "host.docker.internal", "lm-studio"])
            if not is_local:
                raise ConfigurationError("AI_API_KEY must be configured for the selected OpenAI-compatible provider.")
                
        # Specific service validations if URL is supplied
        if self.base_url:
            if "groq.com" in self.base_url and not self.api_key:
                raise ConfigurationError("AI_API_KEY is required for the Groq provider.")
            if "openrouter.ai" in self.base_url and not self.api_key:
                raise ConfigurationError("AI_API_KEY is required for the OpenRouter provider.")

        # Initialize the OpenAI client
        self.client = openai.OpenAI(
            api_key=self.api_key or "no-key-required",
            base_url=self.base_url or None,
            timeout=settings.ai_timeout
        )

    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_stream=True,
            supports_images=True,
            supports_tools=True,
            supports_function_calling=True,
            supports_json_mode=True,
            supports_embeddings=True
        )

    def _convert_messages(self, request: ChatRequest) -> List[dict]:
        openai_messages = []
        if request.prompt_package.system_prompt:
            openai_messages.append({"role": "system", "content": request.prompt_package.system_prompt})
        for msg in request.prompt_package.messages:
            openai_messages.append({"role": msg.role, "content": msg.content})
        return openai_messages

    def _map_exception(self, exc: Exception) -> AIError:
        if isinstance(exc, openai.AuthenticationError):
            return AuthenticationError("Invalid API Key or unauthorized request.", exc)
        elif isinstance(exc, openai.RateLimitError):
            return RateLimitError("API rate limit exceeded.", exc)
        elif isinstance(exc, openai.APITimeoutError):
            return TimeoutError("API request timed out.", exc)
        elif isinstance(exc, openai.APIConnectionError):
            return ProviderUnavailableError("Could not connect to the OpenAI-compatible service endpoint.", exc)
        elif isinstance(exc, openai.NotFoundError):
            return ProviderUnavailableError(f"Requested model or endpoint not found: {str(exc)}", exc)
        elif isinstance(exc, openai.APIError):
            return GenerationError(f"API returned an error: {str(exc)}", exc)
        elif isinstance(exc, AIError):
            return exc
        return GenerationError(f"Unexpected error in OpenAI provider: {str(exc)}", exc)

    def generate_response(self, request: ChatRequest) -> UnifiedResponse:
        try:
            openai_messages = self._convert_messages(request)
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=openai_messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens or settings.ai_max_tokens or None,
                stream=False
            )
            
            choice = response.choices[0]
            usage = None
            if response.usage:
                usage = UsageInfo(
                    input_tokens=response.usage.prompt_tokens,
                    output_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens
                )
                
            return UnifiedResponse(
                content=choice.message.content or "",
                provider="openai",
                model=self.model_name,
                finish_reason=choice.finish_reason,
                usage=usage,
                raw_response=response
            )
        except Exception as e:
            raise self._map_exception(e)

    def generate_stream(self, request: ChatRequest) -> Generator[UnifiedResponse, None, None]:
        try:
            openai_messages = self._convert_messages(request)
            
            response_stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=openai_messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens or settings.ai_max_tokens or None,
                stream=True
            )
            
            for chunk in response_stream:
                if len(chunk.choices) > 0:
                    choice = chunk.choices[0]
                    content = choice.delta.content or ""
                    yield UnifiedResponse(
                        content=content,
                        provider="openai",
                        model=self.model_name,
                        finish_reason=choice.finish_reason,
                        raw_response=chunk
                    )
        except Exception as e:
            raise self._map_exception(e)

    def health_check(self) -> bool:
        try:
            # Send a quick request to verify connection, authentication, and model availability
            self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=1
            )
            return True
        except Exception as e:
            raise self._map_exception(e)

    def list_models(self) -> List[str]:
        try:
            models_list = self.client.models.list()
            return [getattr(m, "id", str(m)) for m in models_list]
        except Exception as e:
            raise self._map_exception(e)
