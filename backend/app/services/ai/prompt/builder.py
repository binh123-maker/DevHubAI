import re
from typing import List, Optional, Any
from app.services.ai.models.response import ChatMessage
from app.services.ai.models.prompt import PromptPackage

class PromptBuilder:
    DEFAULT_SYSTEM_INSTRUCTION = (
        "You are a helpful AI assistant for DevHub AI.\n"
        "You must answer the user's question based strictly on the provided Context Information from their workspace.\n"
        "Never invent facts or use external knowledge not present in the context.\n"
        "If the context contains enough information, provide the best and most accurate answer possible.\n"
        "If the context only partially answers the question, answer using the available information and explicitly state what details are missing.\n"
        "Only refuse to answer when absolutely no relevant context or information is present, in which case you must say exactly:\n"
        "'Tài liệu hiện tại không chứa đủ thông tin để tôi trả lời câu hỏi này.'\n\n"
        "Format your response as clean, plain educational text. Follow these rendering rules strictly:\n"
        "1. Do not expose reasoning and never output <think> blocks.\n"
        "2. Normal educational text must be plain text. Do NOT use Markdown headings (#, ##, etc.), bold (**text**), italic (*text*), or Markdown tables (unless explicitly requested).\n"
        "3. You are ONLY allowed to use Markdown for fenced code blocks (e.g. ```python ... ```) and inline code (e.g. `code`).\n"
        "4. Output all mathematical formulas in LaTeX: enclose block equations in $$...$$ and inline formulas in $...$.\n"
        "5. Preserve mathematical notations and Unicode symbols when appropriate. Keep answers concise and readable."
    )

    @classmethod
    def sanitize_text(cls, text: str) -> str:
        """Sanitize prompt text to prevent injection or errors."""
        if not text:
            return ""
        # Remove null bytes
        return text.replace("\x00", "")

    @classmethod
    def build_prompt(
        cls,
        user_message: str,
        context_text: Optional[str] = None,
        history_messages: Optional[List[Any]] = None,
        system_instruction: Optional[str] = None
    ) -> PromptPackage:
        """
        Build a PromptPackage containing system prompt and message history.
        The last user message contains the grounded context and the current user question.
        """
        system_prompt = system_instruction or cls.DEFAULT_SYSTEM_INSTRUCTION
        system_prompt = cls.sanitize_text(system_prompt)
        
        user_message_sanitized = cls.sanitize_text(user_message)
        
        # Build the final message content with context if present
        if context_text:
            context_sanitized = cls.sanitize_text(context_text)
            final_content = f"Context Information:\n{context_sanitized}\n\nUser Question:\n{user_message_sanitized}\n"
        else:
            final_content = user_message_sanitized

        messages: List[ChatMessage] = []
        
        # Format conversation history
        if history_messages:
            for h in history_messages:
                # Normalizing roles: user -> user, assistant/model -> assistant
                role = "user" if h.role.value == "user" else "assistant"
                messages.append(ChatMessage(role=role, content=cls.sanitize_text(h.content)))

        # Append the final formatted user prompt
        messages.append(ChatMessage(role="user", content=final_content))

        return PromptPackage(
            system_prompt=system_prompt,
            messages=messages,
            context=context_text,
            metadata={}
        )
