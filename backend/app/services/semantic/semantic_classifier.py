from typing import Tuple
from app.services.semantic.rule_based_classifier import RuleBasedSemanticClassifier
from app.services.semantic.base_classifier import SemanticContextWindow

# Maintain backward compatibility by exporting SemanticContextWindow
__all__ = ["SemanticContextWindow", "SemanticClassifier"]

class SemanticClassifier(RuleBasedSemanticClassifier):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def classify_node(self, context: SemanticContextWindow) -> Tuple[str, float]:
        """Backward compatible wrapper for classify."""
        return self.classify(context)
