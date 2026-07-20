import time
from typing import Any, Tuple, List, Optional, Dict
from app.services.semantic.base_classifier import BaseSemanticClassifier, SemanticContextWindow
from app.services.semantic.semantic_rules import SemanticRules
from app.services.semantic.semantic_type_registry import SemanticTypeRegistry
from app.services.semantic.semantic_config import SemanticConfiguration
from app.services.semantic.classification_trace import ClassificationTrace

class RuleBasedSemanticClassifier(BaseSemanticClassifier):
    def __init__(
        self,
        config: Optional[SemanticConfiguration] = None,
        registry: Optional[SemanticTypeRegistry] = None
    ):
        self.config = config or SemanticConfiguration()
        self.registry = registry or SemanticTypeRegistry()
        self.rules = SemanticRules()

    def supports(self, node_type: str) -> bool:
        return True

    def classify(self, context: SemanticContextWindow) -> Tuple[str, float]:
        """Classify the current node and return (semantic_type, confidence)."""
        curr = context.current_node
        if curr is None:
            return "paragraph", 0.0

        node_type = context.get_node_attr(curr, "node_type", "").lower()
        content = context.get_node_attr(curr, "content_text", "") or ""

        enable_context = self.config.ENABLE_CONTEXT_CLASSIFICATION
        enable_meta = self.config.ENABLE_METADATA_REUSE

        # Metadata checks (enabled by config)
        contains_code = context.get_node_metadata(curr, "contains_code", False) if enable_meta else False
        contains_table = context.get_node_metadata(curr, "contains_table", False) if enable_meta else False
        contains_formula = context.get_node_metadata(curr, "contains_formula", False) if enable_meta else False
        contains_list = context.get_node_metadata(curr, "contains_list", False) if enable_meta else False

        # 1. Context-Aware Sequence Rules
        if enable_context:
            # Rule 1: Question -> Paragraph => Answer
            if node_type == "paragraph" or not node_type:
                prev_node = context.previous_node
                if prev_node:
                    prev_content = context.get_node_attr(prev_node, "content_text", "") or ""
                    prev_type = context.get_node_attr(prev_node, "node_type", "").lower()
                    if self.rules.is_question(prev_content) or prev_type == "question":
                        return "answer", 0.95

            # Rule 2: Warning -> List => Warning Procedure (represented as warning type)
            if contains_list or "list" in node_type:
                prev_node = context.previous_node
                if prev_node:
                    prev_content = context.get_node_attr(prev_node, "content_text", "") or ""
                    if self.rules.is_warning(prev_content):
                        return "warning", 0.95

            # Rule 3: Definition -> Code -> Explanation => Code Example (represented as example type)
            if contains_code or "code" in node_type:
                prev_node = context.previous_node
                next_node = context.next_node
                
                prev_is_def = False
                if prev_node:
                    prev_content = context.get_node_attr(prev_node, "content_text", "") or ""
                    prev_is_def = self.rules.is_definition(prev_content)
                    
                next_is_para = False
                if next_node:
                    next_type = context.get_node_attr(next_node, "node_type", "").lower()
                    next_is_para = next_type in ("paragraph", "")
                    
                if prev_is_def and next_is_para:
                    return "example", 0.95

        # 2. Direct Structural Node Type & Metadata
        if "code" in node_type or contains_code:
            return "code", 0.90
        if "table" in node_type or contains_table:
            return "table", 0.90
        if "formula" in node_type or contains_formula:
            return "formula", 0.90

        # 3. Rule matches
        if self.rules.is_warning(content):
            return "warning", 0.85
        if self.rules.is_tip(content):
            return "tip", 0.85
        if self.rules.is_definition(content):
            return "definition", 0.80
        if self.rules.is_algorithm(content):
            return "algorithm", 0.80
        if self.rules.is_summary(content):
            return "summary", 0.80
        if self.rules.is_question(content):
            return "question", 0.85
        if self.rules.is_answer(content):
            return "answer", 0.80
        if self.rules.is_example(content):
            return "example", 0.80

        return "paragraph", 0.50

    def calculate_confidence(self, context: SemanticContextWindow, detected_type: str, base_confidence: float) -> float:
        confidence = base_confidence
        curr = context.current_node
        if curr is None:
            return 0.0

        node_type = context.get_node_attr(curr, "node_type", "").lower()

        parent_heading = context.parent_heading
        if parent_heading:
            heading_text = context.get_node_attr(parent_heading, "content_text", "") or ""
            if detected_type in heading_text.lower():
                confidence += 0.10

        if self.config.ENABLE_METADATA_REUSE:
            contains_code = context.get_node_metadata(curr, "contains_code", False)
            contains_table = context.get_node_metadata(curr, "contains_table", False)
            contains_formula = context.get_node_metadata(curr, "contains_formula", False)
            
            if detected_type == "code" and contains_code:
                confidence += 0.10
            if detected_type == "table" and contains_table:
                confidence += 0.10
            if detected_type == "formula" and contains_formula:
                confidence += 0.10

        if detected_type == "code" and "code" in node_type:
            confidence += 0.10
        if detected_type == "table" and "table" in node_type:
            confidence += 0.10
        if detected_type == "formula" and "formula" in node_type:
            confidence += 0.10

        return min(1.0, max(0.0, confidence))

    def calculate_importance(self, semantic_type: str, content: str) -> float:
        resolved_type = self.registry.get(semantic_type)
        default_imp = resolved_type.default_importance if resolved_type else self.config.DEFAULT_IMPORTANCE

        score = default_imp
        
        word_count = len(content.split())
        if word_count > 100:
            score = min(1.0, score + 0.05)
        elif word_count < 5:
            score = max(0.1, score - 0.20)
            
        return round(score, 2)

    def classify_with_trace(self, context: SemanticContextWindow) -> Tuple[str, float, float, ClassificationTrace]:
        start_time = time.time()
        
        sem_type, base_conf = self.classify(context)
        confidence = self.calculate_confidence(context, sem_type, base_conf)
        
        content = context.get_node_attr(context.current_node, "content_text", "")
        importance = self.calculate_importance(sem_type, content)

        matched_rules = []
        if self.rules.is_warning(content): matched_rules.append("warning_pattern")
        if self.rules.is_tip(content): matched_rules.append("tip_pattern")
        if self.rules.is_definition(content): matched_rules.append("definition_pattern")
        if self.rules.is_algorithm(content): matched_rules.append("algorithm_pattern")
        if self.rules.is_summary(content): matched_rules.append("summary_pattern")
        if self.rules.is_question(content): matched_rules.append("question_pattern")
        if self.rules.is_answer(content): matched_rules.append("answer_pattern")
        if self.rules.is_example(content): matched_rules.append("example_pattern")

        prev_node = context.previous_node
        next_node = context.next_node
        neighbor_ctx = {
            "prev_type": context.get_node_attr(prev_node, "node_type") if prev_node else None,
            "next_type": context.get_node_attr(next_node, "node_type") if next_node else None
        }

        parent_heading_text = context.get_node_attr(context.parent_heading, "content_text") if context.parent_heading else None

        trace = ClassificationTrace(
            semantic_type=sem_type,
            confidence=confidence,
            importance=importance,
            matched_rules=matched_rules,
            metadata_used=context.get_node_attr(context.current_node, "metadata_json", {}),
            neighbor_context=neighbor_ctx,
            heading_context=parent_heading_text,
            classifier_name=self.__class__.__name__,
            execution_time=time.time() - start_time
        )

        return sem_type, confidence, importance, trace
