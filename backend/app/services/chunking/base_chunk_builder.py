from abc import ABC, abstractmethod
from typing import List, Any, Optional

class BaseChunkBuilder(ABC):
    @abstractmethod
    def build_chunks(self, units: List[Any], boundaries: List[Any], context: Optional[Any] = None) -> List[Any]:
        pass

    @abstractmethod
    def merge_chunks(self, chunks: List[Any], context: Optional[Any] = None) -> List[Any]:
        pass

    @abstractmethod
    def split_chunks(self, chunks: List[Any], context: Optional[Any] = None) -> List[Any]:
        pass

    @abstractmethod
    def optimize_chunks(self, chunks: List[Any], context: Optional[Any] = None) -> List[Any]:
        pass

    @abstractmethod
    def validate_chunks(self, chunks: List[Any], context: Optional[Any] = None) -> Any:
        pass

    @abstractmethod
    def supports(self, document_type: str) -> bool:
        pass
