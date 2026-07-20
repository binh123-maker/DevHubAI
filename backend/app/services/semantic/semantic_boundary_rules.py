from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Tuple
from app.services.semantic.semantic_unit import SemanticUnit
from app.services.semantic.semantic_distance import calculate_semantic_distance

class BaseBoundaryRule(ABC):
    @abstractmethod
    def detect(self, unit_a: SemanticUnit, unit_b: SemanticUnit) -> Optional[Dict[str, Any]]:
        """
        Evaluate transition and return a dictionary of properties if boundary is detected.
        """
        pass


class HeadingBoundaryRule(BaseBoundaryRule):
    def detect(self, unit_a: SemanticUnit, unit_b: SemanticUnit) -> Optional[Dict[str, Any]]:
        if unit_a.heading_path != unit_b.heading_path:
            return {
                "boundary_type": "HEADING_BREAK",
                "base_confidence": 0.50,
                "heading_bonus": 0.40,
                "rule_name": "heading_change",
                "priority": 95,
                "reason": "Heading path changed"
            }
        return None


class SectionBoundaryRule(BaseBoundaryRule):
    def detect(self, unit_a: SemanticUnit, unit_b: SemanticUnit) -> Optional[Dict[str, Any]]:
        if unit_a.section_path != unit_b.section_path:
            return {
                "boundary_type": "SECTION_BREAK",
                "base_confidence": 0.45,
                "heading_bonus": 0.35,
                "rule_name": "section_change",
                "priority": 90,
                "reason": "Section path changed"
            }
        return None


class CodeBoundaryRule(BaseBoundaryRule):
    def detect(self, unit_a: SemanticUnit, unit_b: SemanticUnit) -> Optional[Dict[str, Any]]:
        if unit_a.semantic_type != "code" and unit_b.semantic_type == "code":
            return {
                "boundary_type": "CODE_START",
                "base_confidence": 0.50,
                "structure_bonus": 0.30,
                "rule_name": "code_start",
                "priority": 88,
                "reason": "Entering code block"
            }
        elif unit_a.semantic_type == "code" and unit_b.semantic_type != "code":
            return {
                "boundary_type": "CODE_END",
                "base_confidence": 0.50,
                "structure_bonus": 0.30,
                "rule_name": "code_end",
                "priority": 88,
                "reason": "Exiting code block"
            }
        return None


class TableBoundaryRule(BaseBoundaryRule):
    def detect(self, unit_a: SemanticUnit, unit_b: SemanticUnit) -> Optional[Dict[str, Any]]:
        if unit_a.semantic_type != "table" and unit_b.semantic_type == "table":
            return {
                "boundary_type": "TABLE_START",
                "base_confidence": 0.50,
                "structure_bonus": 0.30,
                "rule_name": "table_start",
                "priority": 85,
                "reason": "Entering table block"
            }
        elif unit_a.semantic_type == "table" and unit_b.semantic_type != "table":
            return {
                "boundary_type": "TABLE_END",
                "base_confidence": 0.50,
                "structure_bonus": 0.30,
                "rule_name": "table_end",
                "priority": 85,
                "reason": "Exiting table block"
            }
        return None


class FormulaBoundaryRule(BaseBoundaryRule):
    def detect(self, unit_a: SemanticUnit, unit_b: SemanticUnit) -> Optional[Dict[str, Any]]:
        if unit_a.semantic_type != "formula" and unit_b.semantic_type == "formula":
            return {
                "boundary_type": "FORMULA_START",
                "base_confidence": 0.45,
                "structure_bonus": 0.25,
                "rule_name": "formula_start",
                "priority": 80,
                "reason": "Entering formula block"
            }
        elif unit_a.semantic_type == "formula" and unit_b.semantic_type != "formula":
            return {
                "boundary_type": "FORMULA_END",
                "base_confidence": 0.45,
                "structure_bonus": 0.25,
                "rule_name": "formula_end",
                "priority": 80,
                "reason": "Exiting formula block"
            }
        return None


class WarningBoundaryRule(BaseBoundaryRule):
    def detect(self, unit_a: SemanticUnit, unit_b: SemanticUnit) -> Optional[Dict[str, Any]]:
        if unit_a.semantic_type != "warning" and unit_b.semantic_type == "warning":
            return {
                "boundary_type": "WARNING_START",
                "base_confidence": 0.45,
                "structure_bonus": 0.20,
                "rule_name": "warning_start",
                "priority": 75,
                "reason": "Entering warning block"
            }
        elif unit_a.semantic_type == "warning" and unit_b.semantic_type != "warning":
            return {
                "boundary_type": "WARNING_END",
                "base_confidence": 0.45,
                "structure_bonus": 0.20,
                "rule_name": "warning_end",
                "priority": 75,
                "reason": "Exiting warning block"
            }
        return None


class QuestionAnswerBoundaryRule(BaseBoundaryRule):
    def detect(self, unit_a: SemanticUnit, unit_b: SemanticUnit) -> Optional[Dict[str, Any]]:
        if unit_a.semantic_type == "question" and unit_b.semantic_type == "answer":
            return {
                "boundary_type": "TOPIC_SHIFT",
                "base_confidence": 0.40,
                "semantic_bonus": 0.25,
                "rule_name": "question_to_answer",
                "priority": 70,
                "reason": "Question to answer transition"
            }
        return None


class TopicShiftBoundaryRule(BaseBoundaryRule):
    def detect(self, unit_a: SemanticUnit, unit_b: SemanticUnit) -> Optional[Dict[str, Any]]:
        distance, similarity = calculate_semantic_distance(unit_a, unit_b)
        
        # Rule: Definition -> Example
        if unit_a.semantic_type == "definition" and unit_b.semantic_type == "example":
            return {
                "boundary_type": "TOPIC_SHIFT",
                "base_confidence": 0.40,
                "semantic_bonus": 0.25,
                "rule_name": "definition_to_example",
                "priority": 70,
                "reason": "Definition to example transition"
            }
            
        # Large distance shift
        if distance > 0.40:
            return {
                "boundary_type": "TOPIC_SHIFT",
                "base_confidence": 0.40,
                "semantic_bonus": 0.15,
                "rule_name": "large_semantic_distance",
                "priority": 70,
                "reason": f"Topic shift detected due to large semantic distance ({distance})"
            }
        return None


class FallbackBoundaryRule(BaseBoundaryRule):
    def detect(self, unit_a: SemanticUnit, unit_b: SemanticUnit) -> Optional[Dict[str, Any]]:
        return {
            "boundary_type": "FALLBACK_BOUNDARY",
            "base_confidence": 0.20,
            "rule_name": "fallback_boundary",
            "priority": 20,
            "reason": "Standard fallback paragraph boundary"
        }
