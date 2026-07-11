import logging
from typing import Generator, List, Any
import httpx
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

logger = logging.getLogger(__name__)

@ProviderRegistry.register("ollama")
class OllamaProvider(BaseLLMProvider):
    def __init__(self, model: str) -> None:
        self.model_name = model or settings.ai_model or getattr(settings, "ollama_model", None)
        
        # Resolve base URL from configuration
        raw_base_url = settings.ai_base_url or getattr(settings, "ollama_base_url", None) or "http://localhost:11434"
        self.base_url = raw_base_url.rstrip('/') if raw_base_url else None
        
        if not self.model_name:
            raise ConfigurationError("Ollama model name (AI_MODEL or OLLAMA_MODEL) must be configured.")
        if not self.base_url:
            raise ConfigurationError("Ollama base URL (AI_BASE_URL or OLLAMA_BASE_URL) must be configured.")
        
        # Configure the compatibility client (with /v1 suffix)
        comp_url = f"{self.base_url}/v1"
        self.client = openai.OpenAI(
            api_key="ollama",
            base_url=comp_url,
            timeout=settings.ai_timeout
        )

    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_stream=True,
            supports_images=False,
            supports_tools=False,
            supports_function_calling=False,
            supports_json_mode=False,
            supports_embeddings=False
        )

    def _convert_messages(self, request: ChatRequest) -> List[dict]:
        openai_messages = []
        if request.prompt_package.system_prompt:
            openai_messages.append({"role": "system", "content": request.prompt_package.system_prompt})
        for msg in request.prompt_package.messages:
            openai_messages.append({"role": msg.role, "content": msg.content})
        return openai_messages

    def _map_exception(self, exc: Exception) -> AIError:
        if isinstance(exc, openai.APIConnectionError) or isinstance(exc, httpx.RequestError):
            return ProviderUnavailableError("Ollama service endpoint is unreachable.", exc)
        elif isinstance(exc, openai.APITimeoutError):
            return TimeoutError("Ollama request timed out.", exc)
        elif isinstance(exc, AIError):
            return exc
        return GenerationError(f"Ollama generation failed: {str(exc)}", exc)

    def generate_response(self, request: ChatRequest) -> UnifiedResponse:
        try:
            # 1. Try OpenAI compatibility endpoint first
            openai_messages = self._convert_messages(request)
            try:
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
                    provider="ollama",
                    model=self.model_name,
                    finish_reason=choice.finish_reason,
                    usage=usage,
                    raw_response=response
                )
            except (openai.APIConnectionError, openai.NotFoundError, openai.APIStatusError) as compat_err:
                logger.warning(f"[Ollama] OpenAI compatibility call failed: {str(compat_err)}. Falling back to native /api/chat...")
                
                # 2. Native Ollama /api/chat fallback
                native_url = f"{self.base_url}/api/chat"
                payload = {
                    "model": self.model_name,
                    "messages": openai_messages,
                    "stream": False,
                    "options": {
                        "temperature": request.temperature
                    }
                }
                
                response = httpx.post(native_url, json=payload, timeout=settings.ai_timeout)
                response.raise_for_status()
                data = response.json()
                
                # Extract tokens
                usage = UsageInfo(
                    input_tokens=data.get("prompt_eval_count", 0),
                    output_tokens=data.get("eval_count", 0),
                    total_tokens=data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                )
                
                return UnifiedResponse(
                    content=data.get("message", {}).get("content", ""),
                    provider="ollama",
                    model=self.model_name,
                    finish_reason="stop" if data.get("done") else None,
                    usage=usage,
                    raw_response=data
                )
        except Exception as e:
            raise self._map_exception(e)

    def generate_stream(self, request: ChatRequest) -> Generator[UnifiedResponse, None, None]:
        try:
            # 1. Try OpenAI compatibility endpoint first
            openai_messages = self._convert_messages(request)
            try:
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
                        yield UnifiedResponse(
                            content=choice.delta.content or "",
                            provider="ollama",
                            model=self.model_name,
                            finish_reason=choice.finish_reason,
                            raw_response=chunk
                        )
                return
            except (openai.APIConnectionError, openai.NotFoundError, openai.APIStatusError) as compat_err:
                logger.warning(f"[Ollama Stream] OpenAI compatibility stream failed: {str(compat_err)}. Falling back to native /api/chat...")
                
                # 2. Native Ollama /api/chat stream fallback
                native_url = f"{self.base_url}/api/chat"
                payload = {
                    "model": self.model_name,
                    "messages": openai_messages,
                    "stream": True,
                    "options": {
                        "temperature": request.temperature
                    }
                }
                
                with httpx.stream("POST", native_url, json=payload, timeout=settings.ai_timeout) as r:
                    r.raise_for_status()
                    for line in r.iter_lines():
                        if line:
                            import json
                            data = json.loads(line)
                            content = data.get("message", {}).get("content", "")
                            yield UnifiedResponse(
                                content=content,
                                provider="ollama",
                                model=self.model_name,
                                finish_reason="stop" if data.get("done") else None,
                                raw_response=data
                            )
        except Exception as e:
            raise self._map_exception(e)

    def health_check(self) -> bool:
        try:
            # Check native tags endpoint to check Ollama health
            resp = httpx.get(f"{self.base_url}/api/tags", timeout=3.0)
            return resp.status_code == 200
        except Exception:
            return False

    def list_models(self) -> List[str]:
        try:
            resp = httpx.get(f"{self.base_url}/api/tags", timeout=5.0)
            resp.raise_for_status()
            data = resp.json()
            return [m["name"] for m in data.get("models", [])]
        except Exception as e:
            raise self._map_exception(e)
