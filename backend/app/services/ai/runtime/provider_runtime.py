import os
import time
import logging
from typing import Optional, List, Any, Union, Generator, Dict
from app.services.ai.runtime.provider_capability import Capability
from app.services.ai.runtime.provider_selector import ProviderSelector
from app.services.ai.runtime.provider_result import ProviderResult
from app.services.ai.runtime.provider_statistics import ProviderStatistics
from app.services.ai.runtime.provider_metrics import ProviderMetrics
from app.services.ai.runtime.runtime_timeline import RuntimeTimeline
from app.services.ai.runtime.runtime_trace import RuntimeTrace, TraceStore
from app.services.ai.runtime.runtime_logger import RuntimeLogger
from app.services.ai.policy.policy_engine import PolicyEngine
from app.services.ai.fallback.manager import FallbackManager
from app.services.ai.orchestrator.main import AIOrchestrator
from app.services.ai.models.response import UnifiedResponse

logger = logging.getLogger(__name__)

class ProviderRuntime:
    """
    Main Execution Runtime Engine.
    Executes capabilities via policy-driven candidate chains, fallback management, timeline tracking,
    request tracing, telemetry analytics, and debug metadata.
    """

    _last_execution_data: Optional[Dict[str, Any]] = None

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
        cap_val = capability.value if hasattr(capability, "value") else str(capability)
        current_policy = PolicyEngine.get_policy()

        # 1. Create Runtime Trace
        trace = RuntimeTrace(
            capability=cap_val,
            task_type=cap_val.upper(),
            streaming_enabled=stream
        )

        # 2. Initialize Timeline
        RuntimeTimeline.start(task_type=cap_val.upper(), capability=cap_val)
        RuntimeTimeline.add_step("Policy Engine", {"active_policy": current_policy})

        RuntimeLogger.info(trace.trace_id, "System", cap_val, 0.0, "START")

        # 3. Resolve candidate priority chain
        candidate_chain = ProviderSelector.select_candidate_chain(capability)
        RuntimeTimeline.add_step("Provider Selector", {"candidate_chain": [c["provider"] for c in candidate_chain]})

        from app.services.ai.config.provider_model import ProviderModel
        from app.services.ai.config.provider_env_loader import ProviderEnvLoader

        first_candidate = candidate_chain[0] if candidate_chain else {"provider": "openai", "model": ProviderModel.resolve_model("openai", cap_val)}
        cand_p = first_candidate["provider"]
        cand_m = first_candidate["model"]
        cand_base = ProviderEnvLoader.get_base_url(cand_p) or "N/A"
        res_details = ProviderModel.get_resolution_details(cand_p, cap_val)

        logger.info(
            f"[ProviderRuntime Execution Log]\n"
            f"Provider : {cand_p}\n"
            f"Model : {cand_m}\n"
            f"BaseURL : {cand_base}\n"
            f"Capability : {cap_val}\n"
            f"Policy : {current_policy}"
        )

        RuntimeTimeline.add_step("Model Resolution", {
            "provider": cand_p,
            "resolved_model": cand_m,
            "model_source": res_details.get("model_source", "ProviderProfile"),
            "override_applied": res_details.get("override_applied", False)
        })

        if stream:
            RuntimeTimeline.add_step("Stream Execution", {"selected_provider": first_candidate["provider"], "model": first_candidate["model"]})
            trace.complete(
                selected_provider=first_candidate["provider"],
                selected_model=first_candidate["model"],
                latency_ms=(time.time() - start_time) * 1000,
                streaming_enabled=True,
                model_source=res_details.get("model_source", "ProviderProfile"),
                override_applied=res_details.get("override_applied", False)
            )
            TraceStore.add_trace(trace)
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

        # 4. Synchronous Execution Callable
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

        # 5. Fallback Manager Execution Loop
        try:
            raw_response, fallback_history = FallbackManager.execute_with_fallback(
                candidate_chain=candidate_chain,
                callable_func=_attempt_provider
            )

            total_latency = (time.time() - start_time) * 1000
            was_fallback = len(fallback_history) > 1
            fallback_cnt = max(0, len(fallback_history) - 1)

            input_tokens = raw_response.usage.input_tokens if raw_response.usage else 0
            output_tokens = raw_response.usage.output_tokens if raw_response.usage else 0

            # Complete trace
            trace.complete(
                selected_provider=raw_response.provider,
                selected_model=raw_response.model,
                latency_ms=total_latency,
                prompt_tokens=input_tokens,
                completion_tokens=output_tokens,
                fallback_count=fallback_cnt,
                status="FALLBACK" if was_fallback else "SUCCESS",
                model_source=res_details.get("model_source", "ProviderProfile"),
                override_applied=res_details.get("override_applied", False)
            )
            TraceStore.add_trace(trace)

            RuntimeTimeline.add_step("Execution Completed", {
                "selected_provider": raw_response.provider,
                "model": raw_response.model,
                "latency_ms": round(total_latency, 2),
                "was_fallback": was_fallback,
                "prompt_tokens": input_tokens,
                "completion_tokens": output_tokens
            })

            # Developer Mode Debug Metadata
            dev_mode = os.getenv("DEV_MODE", "true").lower() in ("true", "1", "yes")
            debug_metadata = {}
            if dev_mode:
                debug_metadata = {
                    "trace_id": trace.trace_id,
                    "selected_provider": raw_response.provider,
                    "selected_model": raw_response.model,
                    "latency": round(total_latency, 2),
                    "fallback_count": fallback_cnt,
                    "retry_count": fallback_cnt,
                    "policy": current_policy,
                    "reasoning": getattr(raw_response, "reasoning", None),
                    "health": trace.health_status,
                    "status": trace.status
                }

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
                retry_count=fallback_cnt,
                metadata={
                    "fallback_history": fallback_history,
                    "trace_id": trace.trace_id,
                    "runtime_info": debug_metadata,
                    "_debug": debug_metadata
                }
            )

            # Store last execution data for explainability
            cls._last_execution_data = {
                "trace_id": trace.trace_id,
                "capability": cap_val,
                "policy": current_policy,
                "selected_provider": raw_response.provider,
                "selected_model": raw_response.model,
                "latency_ms": total_latency,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "fallback_history": fallback_history,
                "candidate_chain": candidate_chain
            }

            # Record Statistics & Metrics
            ProviderStatistics.record_execution(
                provider_name=raw_response.provider,
                success=True,
                latency_ms=total_latency,
                prompt_tokens=input_tokens,
                completion_tokens=output_tokens,
                is_fallback=was_fallback
            )
            ProviderMetrics.record_runtime_execution(
                provider_name=raw_response.provider,
                capability=cap_val,
                was_fallback=was_fallback
            )

            RuntimeLogger.info(trace.trace_id, raw_response.provider, cap_val, total_latency, "SUCCESS")
            return result

        except Exception as exc:
            total_latency = (time.time() - start_time) * 1000
            trace.complete(
                selected_provider="error",
                selected_model="error",
                latency_ms=total_latency,
                status="FAILED"
            )
            TraceStore.add_trace(trace)
            RuntimeTimeline.add_step("Execution Failed", {"error": str(exc), "latency_ms": round(total_latency, 2)})
            RuntimeLogger.error(trace.trace_id, f"Execution failed for capability '{cap_val}'", exc)
            raise exc

    @classmethod
    def explain_last_execution(cls) -> str:
        if not cls._last_execution_data:
            return "No recent execution recorded."

        d = cls._last_execution_data
        timeline_md = RuntimeTimeline.generate_markdown()

        explanation = [
            "# Execution Explanation Report",
            f"- **Trace ID**: `{d.get('trace_id', 'N/A')}`",
            f"- **Capability**: `{d['capability']}`",
            f"- **Active Policy**: `{d['policy']}`",
            f"- **Selected Provider**: `{d['selected_provider']}`",
            f"- **Selected Model**: `{d['selected_model']}`",
            f"- **Latency**: `{d['latency_ms']:.1f}ms`",
            f"- **Prompt Tokens**: `{d['input_tokens']}`",
            f"- **Completion Tokens**: `{d['output_tokens']}`",
            f"- **Candidate Chain**: `{[c['provider'] for c in d['candidate_chain']]}`",
            "",
            "## Timeline Details",
            timeline_md
        ]
        return "\n".join(explanation)
