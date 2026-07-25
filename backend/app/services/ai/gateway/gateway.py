from abc import ABC, abstractmethod
from typing import Optional, List, Any, Union, Generator
from app.services.ai.models.response import UnifiedResponse

class BaseAIGateway(ABC):
    @abstractmethod
    def chat(
        self,
        message: str,
        context_text: Optional[str] = None,
        history_messages: Optional[List[Any]] = None,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        metadata: Optional[dict] = None
    ) -> Union[UnifiedResponse, Generator[UnifiedResponse, None, None]]:
        pass

    @abstractmethod
    def reason(
        self,
        problem_statement: str,
        context_text: Optional[str] = None,
        **kwargs
    ) -> UnifiedResponse:
        pass

    @abstractmethod
    def summarize(
        self,
        text_content: str,
        max_length: Optional[int] = None,
        **kwargs
    ) -> UnifiedResponse:
        pass

    @abstractmethod
    def retrieve(
        self,
        query: str,
        context_documents: Optional[str] = None,
        **kwargs
    ) -> UnifiedResponse:
        pass

    @abstractmethod
    def analyze_document(
        self,
        document_text: str,
        analysis_type: str = "general",
        **kwargs
    ) -> UnifiedResponse:
        pass

    @abstractmethod
    def generate_title(
        self,
        conversation_history: List[Any],
        **kwargs
    ) -> UnifiedResponse:
        pass

    @abstractmethod
    def generate_tags(
        self,
        content: str,
        **kwargs
    ) -> UnifiedResponse:
        pass

    @abstractmethod
    def embedding(
        self,
        text_input: Union[str, List[str]],
        **kwargs
    ) -> List[List[float]]:
        pass
