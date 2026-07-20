import json
from typing import Any, Dict, List, Optional

class ClassificationTrace:
    def __init__(
        self,
        semantic_type: str,
        confidence: float,
        importance: float,
        matched_rules: Optional[List[str]] = None,
        matched_keywords: Optional[List[str]] = None,
        metadata_used: Optional[Dict[str, Any]] = None,
        neighbor_context: Optional[Dict[str, Any]] = None,
        heading_context: Optional[str] = None,
        section_context: Optional[str] = None,
        classifier_name: str = "RuleBasedSemanticClassifier",
        execution_time: float = 0.0,
        warnings: Optional[List[str]] = None
    ):
        self.semantic_type = semantic_type
        self.confidence = confidence
        self.importance = importance
        self.matched_rules = matched_rules or []
        self.matched_keywords = matched_keywords or []
        self.metadata_used = metadata_used or {}
        self.neighbor_context = neighbor_context or {}
        self.heading_context = heading_context
        self.section_context = section_context
        self.classifier_name = classifier_name
        self.execution_time = execution_time
        self.warnings = warnings or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "semantic_type": self.semantic_type,
            "confidence": self.confidence,
            "importance": self.importance,
            "matched_rules": self.matched_rules,
            "matched_keywords": self.matched_keywords,
            "metadata_used": self.metadata_used,
            "neighbor_context": self.neighbor_context,
            "heading_context": self.heading_context,
            "section_context": self.section_context,
            "classifier_name": self.classifier_name,
            "execution_time": self.execution_time,
            "warnings": self.warnings
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)

    def pretty_print(self) -> str:
        lines = [
            f"=== Classification Trace ({self.classifier_name}) ===",
            f"Type: {self.semantic_type} (Confidence: {self.confidence:.2f}, Importance: {self.importance:.2f})",
            f"Execution Time: {self.execution_time * 1000:.2f}ms",
            f"Matched Rules: {', '.join(self.matched_rules) if self.matched_rules else 'None'}",
            f"Matched Keywords: {', '.join(self.matched_keywords) if self.matched_keywords else 'None'}",
            f"Metadata Used: {self.metadata_used}",
            f"Neighbor Context: {self.neighbor_context}",
            f"Heading Context: {self.heading_context}",
            f"Section Context: {self.section_context}"
        ]
        if self.warnings:
            lines.append(f"Warnings: {self.warnings}")
        return "\n".join(lines)
