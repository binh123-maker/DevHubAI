from app.services.semantic.semantic_unit import SemanticUnit
from app.services.semantic.semantic_rules import SemanticRules
from app.services.semantic.semantic_classifier import SemanticClassifier, SemanticContextWindow
from app.services.semantic.base_classifier import BaseSemanticClassifier
from app.services.semantic.rule_based_classifier import RuleBasedSemanticClassifier
from app.services.semantic.semantic_type_registry import SemanticTypeRegistry, SemanticType
from app.services.semantic.classification_trace import ClassificationTrace
from app.services.semantic.semantic_config import SemanticConfiguration
from app.services.semantic.semantic_pipeline_context import SemanticPipelineContext
from app.services.semantic.semantic_metrics import SemanticMetrics
from app.services.semantic.semantic_events import (
    SemanticEvent,
    SemanticDetected,
    SemanticRejected,
    SemanticMerged,
    SemanticSplit,
    SemanticValidated,
    SemanticRepair,
)
from app.services.semantic.semantic_unit_detector import SemanticUnitDetector, SemanticRelationshipBuilder

# Phase 10.2 / 10.2A / 10.2B / 10.2C classes
from app.services.semantic.semantic_boundary import SemanticBoundary, BoundaryTrace
from app.services.semantic.semantic_distance import calculate_semantic_distance
from app.services.semantic.boundary_type_registry import BoundaryTypeRegistry, BoundaryType
from app.services.semantic.boundary_metrics import BoundaryMetrics
from app.services.semantic.boundary_events import (
    BoundaryEvent,
    BoundaryDetected,
    BoundaryRejected,
    BoundaryMerged,
    BoundaryValidated,
    BoundaryRepaired,
)
from app.services.semantic.boundary_cache import BoundaryCache
from app.services.semantic.boundary_graph import BoundaryGraph, BoundaryExplanationReport
from app.services.semantic.semantic_boundary_validator import SemanticBoundaryValidator, ValidationReport
from app.services.semantic.semantic_boundary_rules import (
    BaseBoundaryRule,
    HeadingBoundaryRule,
    SectionBoundaryRule,
    CodeBoundaryRule,
    TableBoundaryRule,
    FormulaBoundaryRule,
    WarningBoundaryRule,
    QuestionAnswerBoundaryRule,
    TopicShiftBoundaryRule,
    FallbackBoundaryRule,
)
from app.services.semantic.base_boundary_predictor import BaseBoundaryPredictor
from app.services.semantic.rule_boundary_predictor import RuleBoundaryPredictor
from app.services.semantic.boundary_replay_player import BoundaryReplayPlayer
from app.services.semantic.semantic_boundary_detector import SemanticBoundaryDetector

__all__ = [
    "SemanticUnit",
    "SemanticRules",
    "SemanticClassifier",
    "SemanticContextWindow",
    "BaseSemanticClassifier",
    "RuleBasedSemanticClassifier",
    "SemanticTypeRegistry",
    "SemanticType",
    "ClassificationTrace",
    "SemanticConfiguration",
    "SemanticPipelineContext",
    "SemanticMetrics",
    "SemanticEvent",
    "SemanticDetected",
    "SemanticRejected",
    "SemanticMerged",
    "SemanticSplit",
    "SemanticValidated",
    "SemanticRepair",
    "SemanticUnitDetector",
    "SemanticRelationshipBuilder",
    
    # Phase 10.2 / 10.2A / 10.2B / 10.2C additions
    "SemanticBoundary",
    "BoundaryTrace",
    "calculate_semantic_distance",
    "BoundaryTypeRegistry",
    "BoundaryType",
    "BoundaryMetrics",
    "BoundaryEvent",
    "BoundaryDetected",
    "BoundaryRejected",
    "BoundaryMerged",
    "BoundaryValidated",
    "BoundaryRepaired",
    "BoundaryCache",
    "BoundaryGraph",
    "BoundaryExplanationReport",
    "SemanticBoundaryValidator",
    "ValidationReport",
    "BaseBoundaryRule",
    "HeadingBoundaryRule",
    "SectionBoundaryRule",
    "CodeBoundaryRule",
    "TableBoundaryRule",
    "FormulaBoundaryRule",
    "WarningBoundaryRule",
    "QuestionAnswerBoundaryRule",
    "TopicShiftBoundaryRule",
    "FallbackBoundaryRule",
    "BaseBoundaryPredictor",
    "RuleBoundaryPredictor",
    "BoundaryReplayPlayer",
    "SemanticBoundaryDetector",
]
