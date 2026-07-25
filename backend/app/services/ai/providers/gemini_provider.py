import logging
from typing import Generator, List
import google.generativeai as genai
from google.api_core.exceptions import (
    GoogleAPICallError,
    PermissionDenied,
    ResourceExhausted,
    DeadlineExceeded,
    ServiceUnavailable,
    InvalidArgument
)
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
    TimeoutError,
    ConfigurationError
)

logger = logging.getLogger(__name__)

class GeminiProvider(BaseLLMProvider):
    def __init__(self, model: str = "") -> None:
        cfg = ProviderConfigCenter.get_provider_config("gemini")
        self.model_name = model or cfg.default_model
        self.api_key = cfg.api_key
        if self.api_key:
            genai.configure(api_key=self.api_key)

    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_stream=True,
            supports_images=True,
            supports_tools=False,
            supports_function_calling=False,
            supports_json_mode=False,
            supports_embeddings=False
        )

    def _convert_messages(self, messages) -> list:
        gemini_history = []
        for h in messages[:-1]:
            role = "user" if h.role == "user" else "model"
            gemini_history.append({"role": role, "parts": [h.content]})
        return gemini_history

    def _map_exception(self, exc: Exception) -> AIError:
        if isinstance(exc, InvalidArgument) and "api key" in str(exc).lower():
            return AuthenticationError("Invalid Gemini API Key or permission denied.", exc)
        elif isinstance(exc, PermissionDenied):
            return AuthenticationError("Invalid Gemini API Key or permission denied.", exc)
        elif isinstance(exc, ResourceExhausted):
            return RateLimitError("Gemini API rate limit exceeded.", exc)
        elif isinstance(exc, DeadlineExceeded):
            return TimeoutError("Gemini request timed out.", exc)
        elif isinstance(exc, ServiceUnavailable):
            return ProviderUnavailableError("Gemini service is unavailable.", exc)
        elif isinstance(exc, GoogleAPICallError):
            return GenerationError(f"Gemini API error: {str(exc)}", exc)
        elif isinstance(exc, AIError):
            return exc
        return GenerationError(f"Unexpected error in Gemini provider: {str(exc)}", exc)

    def generate_response(self, request: ChatRequest) -> UnifiedResponse:
        try:
            if not self.api_key:
                raise AuthenticationError("GEMINI_API_KEY is not configured.")
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=request.prompt_package.system_prompt
            )

            gemini_history = self._convert_messages(request.prompt_package.messages)
            chat = model.start_chat(history=gemini_history)

            last_msg = request.prompt_package.messages[-1].content

            config = genai.types.GenerationConfig(
                temperature=request.temperature,
                max_output_tokens=request.max_tokens or None
            )

            response = chat.send_message(last_msg, generation_config=config)

            usage = None
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                usage = UsageInfo(
                    input_tokens=response.usage_metadata.prompt_token_count,
                    output_tokens=response.usage_metadata.candidates_token_count,
                    total_tokens=response.usage_metadata.total_token_count
                )

            return UnifiedResponse(
                content=response.text,
                provider="gemini",
                model=self.model_name,
                finish_reason="stop",
                usage=usage,
                raw_response=response
            )
        except Exception as e:
            raise self._map_exception(e)

    def generate_stream(self, request: ChatRequest) -> Generator[UnifiedResponse, None, None]:
        try:
            if not self.api_key:
                raise AuthenticationError("GEMINI_API_KEY is not configured.")
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=request.prompt_package.system_prompt
            )

            gemini_history = self._convert_messages(request.prompt_package.messages)
            chat = model.start_chat(history=gemini_history)
            last_msg = request.prompt_package.messages[-1].content

            config = genai.types.GenerationConfig(
                temperature=request.temperature,
                max_output_tokens=request.max_tokens or None
            )

            response_stream = chat.send_message(last_msg, generation_config=config, stream=True)
            for chunk in response_stream:
                yield UnifiedResponse(
                    content=chunk.text,
                    provider="gemini",
                    model=self.model_name,
                    finish_reason=None,
                    raw_response=chunk
                )
        except Exception as e:
            raise self._map_exception(e)

    def health_check(self) -> bool:
        try:
            if not self.api_key:
                return False
            model = genai.GenerativeModel(model_name=self.model_name)
            model.generate_content("ping", generation_config={"max_output_tokens": 1})
            return True
        except Exception:
            return False

    def list_models(self) -> List[str]:
        try:
            models = genai.list_models()
            return [m.name for m in models]
        except Exception as e:
            raise self._map_exception(e)
