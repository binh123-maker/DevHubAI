import time
import logging
from typing import Dict, Any, Optional
from app.services.ai.models.prompt import ChatRequest, ChatMessage
from app.services.ai.models.response import UnifiedResponse
from app.services.ai.orchestrator.main import AIOrchestrator

logger = logging.getLogger(__name__)

class ProviderSandbox:
    """
    Developer Sandbox Tool for AI Providers.
    Allows developers to test individual providers, models, and parameters in isolation.
    """

    @classmethod
    def run(
        cls,
        provider: str,
        model: Optional[str] = None,
        prompt: str = "Hello AI",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        start_time = time.time()
        p_id = provider.lower()
        logger.info(f"[ProviderSandbox] Running sandbox test for provider='{p_id}' model='{model}'")

        try:
            if stream:
                gen = AIOrchestrator.generate_stream(
                    user_message=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    override_provider=p_id,
                    override_model=model
                )
                chunks = []
                for chunk in gen:
                    chunks.append(chunk.content)
                total_latency = (time.time() - start_time) * 1000
                full_text = "".join(chunks)
                return {
                    "success": True,
                    "provider": p_id,
                    "model": model or "default",
                    "stream": True,
                    "response": full_text,
                    "latency_ms": round(total_latency, 2)
                }

            response: UnifiedResponse = AIOrchestrator.generate_response(
                user_message=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                override_provider=p_id,
                override_model=model
            )
            total_latency = (time.time() - start_time) * 1000

            return {
                "success": True,
                "provider": response.provider,
                "model": response.model,
                "stream": False,
                "response": response.content,
                "usage": response.usage.model_dump() if response.usage else None,
                "latency_ms": round(total_latency, 2)
            }

        except Exception as exc:
            total_latency = (time.time() - start_time) * 1000
            logger.error(f"[ProviderSandbox] Test failed for provider '{p_id}': {str(exc)}")
            return {
                "success": False,
                "provider": p_id,
                "error": str(exc),
                "latency_ms": round(total_latency, 2)
            }
