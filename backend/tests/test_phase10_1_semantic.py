import uuid
from typing import Tuple
from app.services.semantic.semantic_unit_detector import SemanticUnitDetector
from app.services.semantic.semantic_unit import SemanticUnit
from app.services.semantic.semantic_type_registry import SemanticTypeRegistry, SemanticType
from app.services.semantic.semantic_config import SemanticConfiguration
from app.services.semantic.semantic_pipeline_context import SemanticPipelineContext
from app.services.semantic.semantic_metrics import SemanticMetrics
from app.services.semantic.semantic_events import SemanticDetected, SemanticEvent
from app.services.semantic.base_classifier import BaseSemanticClassifier
from app.services.semantic.semantic_classifier import SemanticContextWindow

def test_metadata_reuse_and_offsets():
    node_id_1 = uuid.uuid4()
    node_id_2 = uuid.uuid4()
    
    mock_nodes = [
        {
            "id": node_id_1,
            "node_type": "heading_1",
            "content_text": "Introduction to Algorithms",
            "content_markdown": "# Introduction to Algorithms",
            "parent_id": None,
            "page_start": 1,
            "page_end": 1,
            "line_start": 1,
            "line_end": 1,
            "char_start": 0,
            "char_end": 26,
            "language": "en",
            "metadata_json": {
                "heading_path": [],
                "section_path": ["Introduction to Algorithms"],
                "document_path": [],
                "token_estimate": 4,
                "contains_code": False
            }
        },
        {
            "id": node_id_2,
            "node_type": "paragraph",
            "content_text": "An algorithm is defined as a set of rules to be followed in calculations.",
            "content_markdown": "An algorithm is defined as a set of rules to be followed in calculations.",
            "parent_id": node_id_1,
            "page_start": 1,
            "page_end": 1,
            "line_start": 3,
            "line_end": 3,
            "char_start": 28,
            "char_end": 101,
            "language": "en",
            "metadata_json": {
                "heading_path": ["Introduction to Algorithms"],
                "section_path": ["Introduction to Algorithms"],
                "document_path": ["Introduction to Algorithms"],
                "token_estimate": 15,
                "contains_code": False
            }
        }
    ]

    detector = SemanticUnitDetector()
    units = detector.detect_semantic_units(mock_nodes)

    assert len(units) == 2
    
    u1, u2 = units[0], units[1]
    assert u1.structure_node_id == node_id_1
    assert u1.page_start == 1
    assert u1.line_start == 1
    assert u1.char_start == 0
    assert u1.char_end == 26
    assert u1.heading_path == []
    assert u1.section_path == ["Introduction to Algorithms"]
    
    assert u2.structure_node_id == node_id_2
    assert u2.heading_path == ["Introduction to Algorithms"]
    assert u2.semantic_type == "definition"
    assert u2.estimated_tokens == 15
    assert u2.importance_score > 0.5


def test_context_aware_classification():
    node_def_id = uuid.uuid4()
    node_code_id = uuid.uuid4()
    node_expl_id = uuid.uuid4()
    
    mock_nodes_code_example = [
        {
            "id": node_def_id,
            "node_type": "paragraph",
            "content_text": "Binary search is defined as an interval-halving search algorithm.",
            "content_markdown": "Binary search is defined as an interval-halving search algorithm.",
            "parent_id": None,
            "page_start": 1,
            "page_end": 1,
            "line_start": 1,
            "line_end": 1,
            "char_start": 0,
            "char_end": 64,
            "language": "en",
            "metadata_json": {}
        },
        {
            "id": node_code_id,
            "node_type": "code_block",
            "content_text": "def binary_search(arr, x):\n  pass",
            "content_markdown": "```python\ndef binary_search(arr, x):\n  pass\n```",
            "parent_id": None,
            "page_start": 1,
            "page_end": 1,
            "line_start": 3,
            "line_end": 4,
            "char_start": 66,
            "char_end": 100,
            "language": "python",
            "metadata_json": {
                "contains_code": True
            }
        },
        {
            "id": node_expl_id,
            "node_type": "paragraph",
            "content_text": "This code implements binary search by dividing search space.",
            "content_markdown": "This code implements binary search by dividing search space.",
            "parent_id": None,
            "page_start": 1,
            "page_end": 1,
            "line_start": 6,
            "line_end": 6,
            "char_start": 102,
            "char_end": 160,
            "language": "en",
            "metadata_json": {}
        }
    ]

    detector = SemanticUnitDetector()
    units = detector.detect_semantic_units(mock_nodes_code_example)

    assert len(units) == 3
    assert units[0].semantic_type == "definition"
    assert units[1].semantic_type == "example"  # Code Example
    assert units[2].semantic_type == "paragraph"

    node_q_id = uuid.uuid4()
    node_a_id = uuid.uuid4()
    mock_nodes_qa = [
        {
            "id": node_q_id,
            "node_type": "paragraph",
            "content_text": "How does quicksort partition the array?",
            "content_markdown": "How does quicksort partition the array?",
            "parent_id": None,
            "page_start": 2,
            "page_end": 2,
            "line_start": 1,
            "line_end": 1,
            "char_start": 0,
            "char_end": 39,
            "language": "en",
            "metadata_json": {}
        },
        {
            "id": node_a_id,
            "node_type": "paragraph",
            "content_text": "It selects a pivot element and partitions other elements into sub-arrays.",
            "content_markdown": "It selects a pivot element and partitions other elements into sub-arrays.",
            "parent_id": None,
            "page_start": 2,
            "page_end": 2,
            "line_start": 3,
            "line_end": 3,
            "char_start": 41,
            "char_end": 114,
            "language": "en",
            "metadata_json": {}
        }
    ]

    units_qa = detector.detect_semantic_units(mock_nodes_qa)
    assert len(units_qa) == 2
    assert units_qa[0].semantic_type == "question"
    assert units_qa[1].semantic_type == "answer"


def test_relationships_and_confidence():
    node_h_id = uuid.uuid4()
    node_p_id = uuid.uuid4()
    
    mock_nodes = [
        {
            "id": node_h_id,
            "node_type": "heading_1",
            "content_text": "System Architecture",
            "content_markdown": "# System Architecture",
            "parent_id": None,
            "page_start": 1,
            "page_end": 1,
            "line_start": 1,
            "line_end": 1,
            "char_start": 0,
            "char_end": 19,
            "language": "en",
            "metadata_json": {}
        },
        {
            "id": node_p_id,
            "node_type": "paragraph",
            "content_text": "This note describes the system components.",
            "content_markdown": "This note describes the system components.",
            "parent_id": node_h_id,
            "page_start": 1,
            "page_end": 1,
            "line_start": 3,
            "line_end": 3,
            "char_start": 21,
            "char_end": 63,
            "language": "en",
            "metadata_json": {}
        }
    ]

    detector = SemanticUnitDetector()
    units = detector.detect_semantic_units(mock_nodes)

    assert len(units) == 2
    u1, u2 = units[0], units[1]
    
    assert u1.next_unit_id == u2.id
    assert u2.previous_unit_id == u1.id
    assert u1.previous_unit_id is None
    assert u2.next_unit_id is None
    assert u2.parent_heading_id == u1.id

    assert 0.0 <= u1.semantic_confidence <= 1.0
    assert 0.0 <= u2.semantic_confidence <= 1.0
    assert 0.0 <= u1.importance_score <= 1.0
    assert 0.0 <= u2.importance_score <= 1.0


# ---------------------------------------------------------------------------
# NEW TEST CASES FOR PHASE 10.1B INFRASTRUCTURE
# ---------------------------------------------------------------------------

def test_semantic_type_registry():
    registry = SemanticTypeRegistry()
    
    # Verify default types exist
    assert registry.exists("definition")
    assert registry.exists("warning")
    assert registry.resolve_alias("caution") == "warning"
    
    # Priority sorting
    sorted_types = registry.list_types()
    assert sorted_types[0].priority < sorted_types[-1].priority
    
    # Custom registration
    custom_type = SemanticType(
        name="api_endpoint",
        display_name="API Endpoint",
        category="technical",
        description="REST or gRPC endpoint",
        default_importance=0.90,
        priority=1,
        aliases=["endpoint", "route"]
    )
    registry.register(custom_type)
    assert registry.exists("api_endpoint")
    assert registry.resolve_alias("route") == "api_endpoint"
    assert registry.get("api_endpoint").default_importance == 0.90
    
    # Unregistration
    registry.unregister("api_endpoint")
    assert not registry.exists("api_endpoint")


def test_pipeline_context_metrics_events():
    config = SemanticConfiguration(min_confidence=0.1)
    context = SemanticPipelineContext(
        document_id=uuid.uuid4(),
        document_version_id=uuid.uuid4(),
        workspace_id=uuid.uuid4(),
        semantic_config=config,
        tracing_enabled=True
    )
    
    metrics = SemanticMetrics()
    
    mock_nodes = [
        {
            "id": uuid.uuid4(),
            "node_type": "paragraph",
            "content_text": "Warning: disconnect power before service.",
            "content_markdown": "Warning: disconnect power before service.",
            "parent_id": None,
            "page_start": 1,
            "page_end": 1,
            "line_start": 1,
            "line_end": 1,
            "char_start": 0,
            "char_end": 41,
            "language": "en",
            "metadata_json": {}
        }
    ]
    
    detector = SemanticUnitDetector(config=config, context=context, metrics=metrics)
    units = detector.detect_semantic_units(mock_nodes)
    
    # Validate context caching
    assert len(context.semantic_units) == 1
    assert len(context.traces) == 1
    assert len(context.events) == 1
    assert isinstance(context.events[0], SemanticDetected)
    
    # Validate metrics
    assert metrics.total_nodes == 1
    assert metrics.total_units == 1
    assert metrics.semantic_distribution["warning"] == 1
    assert metrics.average_confidence > 0.0
    assert metrics.processing_time >= 0.0
    
    # Check trace representation
    trace = list(context.traces.values())[0]
    assert trace.semantic_type == "warning"
    assert "warning_pattern" in trace.matched_rules
    assert isinstance(trace.to_dict(), dict)
    assert "Classification Trace" in trace.pretty_print()


class MockCustomClassifier(BaseSemanticClassifier):
    def supports(self, node_type: str) -> bool:
        return True
    def classify(self, context: SemanticContextWindow) -> Tuple[str, float]:
        return "custom_type", 0.99
    def calculate_confidence(self, context: SemanticContextWindow, detected_type: str, base_confidence: float) -> float:
        return 1.0
    def calculate_importance(self, semantic_type: str, content: str) -> float:
        return 0.95

def test_dependency_injection():
    # Inject MockCustomClassifier
    custom_classifier = MockCustomClassifier()
    detector = SemanticUnitDetector(classifier=custom_classifier)
    
    mock_nodes = [
        {
            "id": uuid.uuid4(),
            "node_type": "paragraph",
            "content_text": "Testing pluggable architecture",
            "content_markdown": "Testing pluggable architecture",
            "parent_id": None,
            "page_start": 1,
            "page_end": 1,
            "line_start": 1,
            "line_end": 1,
            "char_start": 0,
            "char_end": 30,
            "metadata_json": {}
        }
    ]
    
    units = detector.detect_semantic_units(mock_nodes)
    assert len(units) == 1
    assert units[0].semantic_type == "custom_type"
    assert units[0].semantic_confidence == 1.0
    assert units[0].importance_score == 0.95
