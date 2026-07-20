from abc import ABC, abstractmethod
from typing import Any, Tuple, Optional

class SemanticContextWindow:
    def __init__(
        self,
        current_node: Any,
        previous_node: Optional[Any] = None,
        next_node: Optional[Any] = None,
        parent_heading: Optional[Any] = None,
        section: Optional[Any] = None
    ):
        self.current_node = current_node
        self.previous_node = previous_node
        self.next_node = next_node
        self.parent_heading = parent_heading
        self.section = section

    def get_node_attr(self, node: Any, attr: str, default: Any = None) -> Any:
        """Helper to get attribute from either dict or object representation of a node."""
        if node is None:
            return default
        if isinstance(node, dict):
            return node.get(attr, default)
        return getattr(node, attr, default)

    def get_node_metadata(self, node: Any, key: str, default: Any = None) -> Any:
        """Helper to get values from metadata_json or fallback to node attributes."""
        if node is None:
            return default
        meta = self.get_node_attr(node, "metadata_json", {}) or {}
        return meta.get(key, default)


class BaseSemanticClassifier(ABC):
    @abstractmethod
    def classify(self, context: SemanticContextWindow) -> Tuple[str, float]:
        """
        Classifies the current node in the given context window.
        Returns:
            (semantic_type, confidence)
        """
        pass

    @abstractmethod
    def calculate_confidence(self, context: SemanticContextWindow, detected_type: str, base_confidence: float) -> float:
        """
        Calculates/refines the confidence score based on context, rules, and metadata agreement.
        """
        pass

    @abstractmethod
    def calculate_importance(self, semantic_type: str, content: str) -> float:
        """
        Calculates usefulness (importance) score for a given unit.
        """
        pass

    @abstractmethod
    def supports(self, node_type: str) -> bool:
        """
        Checks if this classifier supports a specific node type.
        """
        pass
