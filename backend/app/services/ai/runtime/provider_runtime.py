import logging
import time
from typing import Optional, List, Any, Union, Generator
from app.services.ai.runtime.provider_capability import Capability
from app.services.ai.runtime.provider_selector import ProviderSelector
from app.services.ai.runtime.provider_result import ProviderResult
from app.services.ai.runtime.provider_statistics import ProviderStatistics
from app.services.ai.runtime.provider_metrics import ProviderMetrics
from app.services.ai.runtime.provider_events import (
    ProviderSelectedEvent,
    ProviderStartedEvent,
    ProviderFinishedEvent,
    ProviderFailedEvent,
    RuntimeCompletedEvent
)
from app.services.ai.fallback.manager import FallbackManager
from app.services.ai.orchestrator.main import AIOrchestrator
from app.services.ai.models.response import UnifiedResponse

logger = logging.getLogger(__name__)

class ProviderRuntime:
    """
    Main Execution Runtime Engine for Phase 10.7B.
    Caller services invoke `runtime.execute()` with a target `Capability`.
    No provider-specific classes are exposed to caller services.
    """

    @classmethod
    def execute(
        cls,
        capability: Capability,
        user_message: str,
        context_text: Optional[str] = None,
        history_messages: Optional[List[Any]] = None,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Union[ProviderResult, Generator[UnifiedResponse, None, None]]:

        start_time = time.time()
        logger.info(f"[ProviderRuntime] Executing capability '{capability.value}' (stream={stream})")

        # 1. Resolve candidate priority chain
        candidate_chain = ProviderSelector.select_candidate_chain(capability)

        if stream:
            # For stream requests, resolve first healthy candidate
            first_candidate = candidate_chain[0] if candidate_chain else {"provider": "openai", "model": "gpt-4o"}
            return AIOrchestrator.generate_stream(
                user_message=user_message,
                context_text=context_text,
                history_messages=history_messages,
                system_instruction=system_instruction,
                temperature=temperature,
                max_tokens=max_tokens,
                override_provider=first_candidate["provider"],
                override_model=first_candidate["model"]
            )

        # 2. Synchronous Execution Callable
        def _attempt_provider(provider: str, model: str) -> UnifiedResponse:
            return AIOrchestrator.generate_response(
                user_message=user_message,
                context_text=context_text,
                history_messages=history_messages,
                system_instruction=system_instruction,
                temperature=temperature,
                max_tokens=max_tokens,
                override_provider=provider,
                override_model=model
            )

        # 3. Fallback Manager Execution Loop
        try:
            raw_response, fallback_history = FallbackManager.execute_with_fallback(
                candidate_chain=candidate_chain,
                callable_func=_attempt_provider
            )

            total_latency = (time.time() - start_time) * 1000
            was_fallback = len(fallback_history) > 1

            # 4. Normalize to Unified ProviderResult
            input_tokens = raw_response.usage.input_tokens if raw_response.usage else 0
            output_tokens = raw_response.usage.output_tokens if raw_response.usage else 0

            result = ProviderResult(
                provider_name=raw_response.provider,
                model=raw_response.model,
                capability=capability,
                response=raw_response.content,
                reasoning=getattr(raw_response, "reasoning", None),
                citations=getattr(raw_response, "citations", []),
                usage=raw_response.usage,
                latency_ms=total_latency,
                finish_reason=raw_response.finish_reason or "stop",
                success=True,
                retry_count=max(0, len(fallback_history) - 1),
                metadata={"fallback_history": fallback_history}
            )

            # 5. Record Statistics & Metrics
            ProviderStatistics.record_execution(
                provider_name=raw_response.provider,
                success=True,
                latency_ms=total_latency,
                prompt_tokens=input_tokens,
                completion_tokens=output_tokens
            )
            ProviderMetrics.record_runtime_execution(
                provider_name=raw_response.provider,
                capability=capability.value,
                was_fallback=was_fallback
            )

            logger.info(f"[ProviderRuntime] Execution completed via provider '{raw_response.provider}' in {total_latency:.1f}ms")
            return result

        except Exception as exc:
            total_latency = (time.time() - start_time) * 1000
            logger.error(f"[ProviderRuntime] Execution failed for capability '{capability.value}': {str(exc)}")
            raise exc
