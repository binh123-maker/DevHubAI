import time
import logging
from typing import Generator, List, Optional, Any
from app.services.ai.router.main import AIRouter
from app.services.ai.prompt.builder import PromptBuilder
from app.services.ai.factory.main import LLMFactory
from app.services.ai.retry.policy import RetryPolicy
from app.services.ai.circuit_breaker.breaker import CircuitBreaker
from app.services.ai.metrics.collector import MetricsCollector
from app.services.ai.models.prompt import ChatRequest, PromptPackage
from app.services.ai.models.response import UnifiedResponse, ChatMessage
from app.services.ai.exceptions import AIError, TimeoutError, RateLimitError

logger = logging.getLogger(__name__)

# Shared resilience components
_circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30.0)
_retry_policy = RetryPolicy(
    max_retries=2,
    delay=1.0,
    backoff_factor=2.0,
    retryable_errors=(TimeoutError, RateLimitError)
)

class AIOrchestrator:
    @staticmethod
    def generate_response(
        user_message: str,
        context_text: Optional[str] = None,
        history_messages: Optional[List[Any]] = None,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> UnifiedResponse:
        """
        Orchestrates prompt building, provider routing, factory resolution,
        retry policy, circuit breaker, and metrics logging.
        """
        # 1. Route to provider selection
        selection = AIRouter.select_provider()

        # 2. Build prompt package
        prompt_package = PromptBuilder.build_prompt(
            user_message=user_message,
            context_text=context_text,
            history_messages=history_messages,
            system_instruction=system_instruction
        )

        # 3. Resolve provider instance
        provider = LLMFactory.get_provider(selection)

        # 4. Construct request
        request = ChatRequest(
            prompt_package=prompt_package,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False
        )

        start_time = time.time()
        calls = 0
        
        def _call_provider():
            nonlocal calls
            calls += 1
            return provider.generate_response(request)

        try:
            # Wrap execution with circuit breaker and retry policy
            response = _circuit_breaker.call(
                _retry_policy.execute,
                _call_provider
            )
            
            latency = (time.time() - start_time) * 1000
            response.latency_ms = latency
            
            # Record metrics
            input_tokens = response.usage.input_tokens if response.usage else 0
            output_tokens = response.usage.output_tokens if response.usage else 0
            MetricsCollector.record(
                provider=response.provider,
                model=response.model,
                latency_ms=latency,
                prompt_tokens=input_tokens,
                completion_tokens=output_tokens,
                retry_count=max(0, calls - 1)
            )
            
            return response
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            error_type = type(e).__name__
            MetricsCollector.record(
                provider=selection.provider,
                model=selection.model,
                latency_ms=latency,
                retry_count=max(0, calls - 1),
                error_type=error_type
            )
            raise e

    @staticmethod
    def generate_stream(
        user_message: str,
        context_text: Optional[str] = None,
        history_messages: Optional[List[Any]] = None,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Generator[UnifiedResponse, None, None]:
        """
        Orchestrator stream generator interface.
        Wrapped with circuit breaker but bypasses general retry policies
        due to streaming connection constraints.
        """
        selection = AIRouter.select_provider()
        prompt_package = PromptBuilder.build_prompt(
            user_message=user_message,
            context_text=context_text,
            history_messages=history_messages,
            system_instruction=system_instruction
        )
        provider = LLMFactory.get_provider(selection)
        request = ChatRequest(
            prompt_package=prompt_package,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )

        start_time = time.time()
        try:
            def _call_stream():
                return provider.generate_stream(request)

            stream_gen = _circuit_breaker.call(_call_stream)
            for chunk in stream_gen:
                yield chunk
                
            latency = (time.time() - start_time) * 1000
            MetricsCollector.record(
                provider=selection.provider,
                model=selection.model,
                latency_ms=latency,
                retry_count=0
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            MetricsCollector.record(
                provider=selection.provider,
                model=selection.model,
                latency_ms=latency,
                retry_count=0,
                error_type=type(e).__name__
            )
            raise e
