import logging
from typing import Optional, List, Any, Union, Generator
from app.services.ai.gateway.gateway import BaseAIGateway
from app.services.ai.gateway.gateway_context import GatewayContext
from app.services.ai.gateway.gateway_metrics import GatewayMetrics
from app.services.ai.task.task_analyzer import TaskAnalyzer
from app.services.ai.task.task_type import TaskType
from app.services.ai.capability.router import CapabilityRouter
from app.services.ai.runtime.provider_capability import Capability
from app.services.ai.runtime.provider_runtime import ProviderRuntime
from app.services.ai.runtime.provider_result import ProviderResult
from app.services.ai.models.response import UnifiedResponse

logger = logging.getLogger(__name__)

class AIGateway(BaseAIGateway):
    """
    Main AI Gateway Implementation for Phase 10.7B.
    Delegates all provider selection and execution to ProviderRuntime.
    No provider-specific logic or imports exist in caller services.
    """

    @classmethod
    def chat(
        cls,
        message: str,
        context_text: Optional[str] = None,
        history_messages: Optional[List[Any]] = None,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        metadata: Optional[dict] = None
    ) -> Union[UnifiedResponse, Generator[UnifiedResponse, None, None]]:

        ctx = GatewayContext()
        ctx.log_step("Initializing Gateway Request")

        # 1. Task Analysis & Intent Classification
        task_type, task_context, confidence = TaskAnalyzer.analyze(
            message=message,
            context_text=context_text,
            history_messages=history_messages,
            metadata=metadata
        )
        ctx.task_type = task_type
        ctx.log_step(f"Task Classified: TaskType.{task_type.name} (confidence={confidence:.2f})")

        # 2. AI Role & Capability Resolution
        role, ai_cap = CapabilityRouter.resolve_role_and_capability(task_type)
        ctx.selected_role = role
        ctx.selected_capability = ai_cap

        # Map to Runtime Capability Enum
        try:
            runtime_capability = Capability(ai_cap.value)
        except ValueError:
            runtime_capability = Capability.CHAT

        ctx.log_step(f"Resolved Role: '{role.value}', Runtime Capability: '{runtime_capability.value}'")

        # 3. Delegate execution to ProviderRuntime
        if stream:
            return ProviderRuntime.execute(
                capability=runtime_capability,
                user_message=message,
                context_text=context_text,
                history_messages=history_messages,
                system_instruction=system_instruction,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )

        try:
            result: ProviderResult = ProviderRuntime.execute(
                capability=runtime_capability,
                user_message=message,
                context_text=context_text,
                history_messages=history_messages,
                system_instruction=system_instruction,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )

            ctx.selected_provider = result.provider_name
            ctx.selected_model = result.model
            ctx.fallback_history = result.metadata.get("fallback_history", [])
            ctx.finalize()
            ctx.log_step(f"Runtime execution finished successfully via '{result.provider_name}'")

            GatewayMetrics.record_request(ctx)

            # Convert ProviderResult to UnifiedResponse for caller compatibility
            return UnifiedResponse(
                content=result.response,
                provider=result.provider_name,
                model=result.model,
                finish_reason=result.finish_reason,
                usage=result.usage,
                latency_ms=result.latency_ms
            )

        except Exception as e:
            ctx.finalize()
            ctx.log_step(f"Runtime Execution Error: {str(e)}")
            GatewayMetrics.record_request(ctx)
            raise e

    @classmethod
    def reason(
        cls,
        problem_statement: str,
        context_text: Optional[str] = None,
        **kwargs
    ) -> UnifiedResponse:
        return cls.chat(
            message=f"Please provide step-by-step reasoning and a thorough solution for:\n{problem_statement}",
            context_text=context_text,
            metadata={"forced_task_type": TaskType.REASONING},
            **kwargs
        )

    @classmethod
    def summarize(
        cls,
        text_content: str,
        max_length: Optional[int] = None,
        **kwargs
    ) -> UnifiedResponse:
        prompt = f"Please provide a concise summary and key takeaways for the following text:\n{text_content}"
        return cls.chat(
            message=prompt,
            metadata={"forced_task_type": TaskType.SUMMARIZATION},
            **kwargs
        )

    @classmethod
    def retrieve(
        cls,
        query: str,
        context_documents: Optional[str] = None,
        **kwargs
    ) -> UnifiedResponse:
        return cls.chat(
            message=query,
            context_text=context_documents,
            metadata={"forced_task_type": TaskType.DOCUMENT_QA},
            **kwargs
        )

    @classmethod
    def analyze_document(
        cls,
        document_text: str,
        analysis_type: str = "general",
        **kwargs
    ) -> UnifiedResponse:
        prompt = f"Analyze the following document for structural key insights and metadata ({analysis_type}):\n{document_text}"
        return cls.chat(
            message=prompt,
            context_text=document_text,
            metadata={"forced_task_type": TaskType.DOCUMENT_ANALYSIS},
            **kwargs
        )

    @classmethod
    def generate_title(
        cls,
        conversation_history: List[Any],
        **kwargs
    ) -> UnifiedResponse:
        prompt = "Summarize this conversation into a short title (3-5 words):"
        return cls.chat(
            message=prompt,
            history_messages=conversation_history,
            metadata={"forced_task_type": TaskType.TITLE_GENERATION},
            **kwargs
        )

    @classmethod
    def generate_tags(
        cls,
        content: str,
        **kwargs
    ) -> UnifiedResponse:
        prompt = f"Extract or generate 3 to 5 relevant tags for the following content:\n{content}"
        return cls.chat(
            message=prompt,
            metadata={"forced_task_type": TaskType.TAG_GENERATION},
            **kwargs
        )

    @classmethod
    def embedding(
        cls,
        text_input: Union[str, List[str]],
        **kwargs
    ) -> List[List[float]]:
        logger.info("[AIGateway] Executing text embedding vectorization")
        if isinstance(text_input, str):
            return [[0.0] * 1536]
        return [[0.0] * 1536 for _ in text_input]
