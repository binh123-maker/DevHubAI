import logging
from typing import Generator, List
import openai
from app.services.ai.config.provider_config import ProviderConfigCenter
from app.services.ai.providers.base import BaseLLMProvider
from app.services.ai.models.capabilities import ProviderCapabilities
from app.services.ai.models.prompt import ChatRequest
from app.services.ai.models.response import UnifiedResponse, UsageInfo
from app.services.ai.exceptions import (
    AIError,
    AuthenticationError,
    ProviderUnavailableError,
    GenerationError,
    RateLimitError,
    TimeoutError
)

logger = logging.getLogger(__name__)

class OpenRouterProvider(BaseLLMProvider):
    def __init__(self, model: str = "") -> None:
        cfg = ProviderConfigCenter.get_provider_config("openrouter")
        self.model_name = model or cfg.default_model
        self.api_key = cfg.api_key
        self.base_url = cfg.base_url or "https://openrouter.ai/api/v1"

        self.client = openai.OpenAI(
            api_key=self.api_key or "no-key-configured",
            base_url=self.base_url,
            timeout=cfg.timeout
        )

    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_stream=True,
            supports_images=True,
            supports_tools=True,
            supports_function_calling=True,
            supports_json_mode=True,
            supports_embeddings=False
        )

    def _convert_messages(self, request: ChatRequest) -> List[dict]:
        messages = []
        if request.prompt_package.system_prompt:
            messages.append({"role": "system", "content": request.prompt_package.system_prompt})
        for msg in request.prompt_package.messages:
            messages.append({"role": msg.role, "content": msg.content})
        return messages

    def _map_exception(self, exc: Exception) -> AIError:
        if isinstance(exc, openai.AuthenticationError):
            return AuthenticationError("Invalid OpenRouter API Key or unauthorized request.", exc)
        elif isinstance(exc, openai.RateLimitError):
            return RateLimitError("OpenRouter API rate limit exceeded.", exc)
        elif isinstance(exc, openai.APITimeoutError):
            return TimeoutError("OpenRouter API request timed out.", exc)
        elif isinstance(exc, openai.APIConnectionError):
            return ProviderUnavailableError("Could not connect to OpenRouter endpoint.", exc)
        elif isinstance(exc, openai.NotFoundError):
            return ProviderUnavailableError(f"Requested OpenRouter model not found: {str(exc)}", exc)
        elif isinstance(exc, AIError):
            return exc
        return GenerationError(f"OpenRouter provider error: {str(exc)}", exc)

    def generate_response(self, request: ChatRequest) -> UnifiedResponse:
        try:
            if not self.api_key:
                raise AuthenticationError("OPENROUTER_API_KEY is not configured.")
            or_messages = self._convert_messages(request)
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=or_messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens or None,
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
                provider="openrouter",
                model=self.model_name,
                finish_reason=choice.finish_reason,
                usage=usage,
                raw_response=response
            )
        except Exception as e:
            raise self._map_exception(e)

    def generate_stream(self, request: ChatRequest) -> Generator[UnifiedResponse, None, None]:
        try:
            if not self.api_key:
                raise AuthenticationError("OPENROUTER_API_KEY is not configured.")
            or_messages = self._convert_messages(request)
            response_stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=or_messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens or None,
                stream=True
            )
            for chunk in response_stream:
                if len(chunk.choices) > 0:
                    choice = chunk.choices[0]
                    content = choice.delta.content or ""
                    yield UnifiedResponse(
                        content=content,
                        provider="openrouter",
                        model=self.model_name,
                        finish_reason=choice.finish_reason,
                        raw_response=chunk
                    )
        except Exception as e:
            raise self._map_exception(e)

    def health_check(self) -> bool:
        try:
            if not self.api_key:
                return False
            self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=1
            )
            return True
        except Exception:
            return False

    def list_models(self) -> List[str]:
        try:
            models_list = self.client.models.list()
            return [getattr(m, "id", str(m)) for m in models_list]
        except Exception as e:
            raise self._map_exception(e)
