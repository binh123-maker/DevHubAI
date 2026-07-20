import uuid
import pytest
from app.services.semantic.semantic_unit import SemanticUnit
from app.services.semantic.semantic_boundary import SemanticBoundary
from app.services.semantic.semantic_boundary_detector import SemanticBoundaryDetector
from app.services.semantic.boundary_type_registry import BoundaryTypeRegistry, BoundaryType
from app.services.semantic.boundary_metrics import BoundaryMetrics
from app.services.semantic.boundary_cache import BoundaryCache
from app.services.semantic.boundary_graph import BoundaryGraph
from app.services.semantic.semantic_boundary_validator import SemanticBoundaryValidator
from app.services.semantic.semantic_pipeline_context import SemanticPipelineContext
from app.services.semantic.semantic_config import SemanticConfiguration
from app.services.semantic.base_boundary_predictor import BaseBoundaryPredictor
from app.services.semantic.boundary_replay_player import BoundaryReplayPlayer

def test_boundary_detection_rules_and_priorities():
    unit_id_1 = uuid.uuid4()
    unit_id_2 = uuid.uuid4()
    unit_id_3 = uuid.uuid4()
    unit_id_4 = uuid.uuid4()
    unit_id_5 = uuid.uuid4()
    
    units = [
        SemanticUnit(
            id=unit_id_1,
            structure_node_id=uuid.uuid4(),
            semantic_type="definition",
            content="A binary tree is a tree data structure in which each node has at most two children.",
            heading_path=["Data Structures"],
            section_path=["Data Structures", "Trees"],
            language="en",
            page_start=1,
            page_end=1,
            line_start=1,
            line_end=2,
            char_start=0,
            char_end=84,
            importance_score=0.85
        ),
        SemanticUnit(
            id=unit_id_2,
            structure_node_id=uuid.uuid4(),
            semantic_type="code",
            content="class Node:\n    def __init__(self):\n        self.left = None",
            heading_path=["Data Structures"],
            section_path=["Data Structures", "Trees"],
            language="en",
            page_start=1,
            page_end=1,
            line_start=4,
            line_end=6,
            char_start=86,
            char_end=150,
            importance_score=0.70
        ),
        SemanticUnit(
            id=unit_id_3,
            structure_node_id=uuid.uuid4(),
            semantic_type="table",
            content="| Key | Value |\n|---|---|",
            heading_path=["Advanced structures"],
            section_path=["Advanced structures", "Tables"],
            language="en",
            page_start=2,
            page_end=2,
            line_start=1,
            line_end=2,
            char_start=152,
            char_end=200,
            importance_score=0.70
        ),
        SemanticUnit(
            id=unit_id_4,
            structure_node_id=uuid.uuid4(),
            semantic_type="question",
            content="What is the height of an empty tree?",
            heading_path=["Advanced structures"],
            section_path=["Advanced structures", "Tables"],
            language="en",
            page_start=2,
            page_end=2,
            line_start=4,
            line_end=4,
            char_start=202,
            char_end=238,
            importance_score=0.65
        ),
        SemanticUnit(
            id=unit_id_5,
            structure_node_id=uuid.uuid4(),
            semantic_type="answer",
            content="The height of an empty tree is defined as -1.",
            heading_path=["Advanced structures"],
            section_path=["Advanced structures", "Tables"],
            language="en",
            page_start=2,
            page_end=2,
            line_start=5,
            line_end=5,
            char_start=240,
            char_end=285,
            importance_score=0.65
        ),
    ]

    detector = SemanticBoundaryDetector()
    boundaries = detector.detect_boundaries(units)

    assert len(boundaries) == 5

    # 1. Transition 1: definition -> code => CODE_START
    assert boundaries[0].boundary_type == "CODE_START"
    assert boundaries[0].previous_unit_id == unit_id_1
    assert boundaries[0].next_unit_id == unit_id_2
    assert boundaries[0].priority == 88

    # 2. Transition 2: code -> table with Heading Change => HEADING_BREAK
    assert boundaries[1].boundary_type == "HEADING_BREAK"
    assert boundaries[1].priority == 95

    # 3. Transition 3: table -> question => TABLE_END (exiting table block)
    assert boundaries[2].boundary_type == "TABLE_END"
    assert boundaries[2].priority == 85

    # 4. Transition 4: question -> answer => TOPIC_SHIFT (due to question_to_answer rule)
    assert boundaries[3].boundary_type == "TOPIC_SHIFT"
    assert boundaries[3].priority == 70

    # 5. Last boundary: DOCUMENT_END
    assert boundaries[4].boundary_type == "DOCUMENT_END"
    assert boundaries[4].next_unit_id is None
    assert boundaries[4].priority == 100


def test_boundary_type_registry():
    registry = BoundaryTypeRegistry()
    
    assert registry.exists("HEADING_BREAK")
    assert registry.resolve_alias("heading_change") == "HEADING_BREAK"
    assert registry.priority("HEADING_BREAK") == 95

    custom_boundary = BoundaryType(
        name="CUSTOM_BREAK",
        priority=82,
        aliases=["my_break"],
        description="Custom boundary rule"
    )
    registry.register(custom_boundary)
    assert registry.exists("CUSTOM_BREAK")
    assert registry.resolve_alias("my_break") == "CUSTOM_BREAK"
    assert registry.priority("CUSTOM_BREAK") == 82

    types = registry.list_types()
    assert types[0].priority > types[-1].priority

    registry.unregister("CUSTOM_BREAK")
    assert not registry.exists("CUSTOM_BREAK")


def test_boundary_metrics_and_events():
    config = SemanticConfiguration()
    context = SemanticPipelineContext(semantic_config=config)
    metrics = BoundaryMetrics()
    
    detector = SemanticBoundaryDetector(context=context, metrics=metrics)
    
    unit_id_1 = uuid.uuid4()
    unit_id_2 = uuid.uuid4()
    units = [
        SemanticUnit(
            id=unit_id_1,
            structure_node_id=uuid.uuid4(),
            semantic_type="paragraph",
            content="Para 1",
            heading_path=["Intro"],
            section_path=["Intro"],
            language="en",
            page_start=1,
            page_end=1,
            line_start=1,
            line_end=1,
            char_start=0,
            char_end=6
        ),
        SemanticUnit(
            id=unit_id_2,
            structure_node_id=uuid.uuid4(),
            semantic_type="code",
            content="import sys",
            heading_path=["Intro"],
            section_path=["Intro"],
            language="en",
            page_start=1,
            page_end=1,
            line_start=2,
            line_end=2,
            char_start=8,
            char_end=18
        )
    ]
    
    boundaries = detector.detect_boundaries(units)
    assert len(boundaries) == 2

    # Check metrics
    assert metrics.total_boundaries == 2
    assert metrics.code_boundaries == 1
    assert metrics.average_confidence > 0.0
    assert metrics.boundary_density == 1.0
    assert isinstance(metrics.to_dict(), dict)
    
    # Extended metrics validation (10.2B / C)
    assert "CODE_START" in metrics.boundary_distribution
    assert "code_start" in metrics.rule_hit_distribution
    assert "code_start" in metrics.execution_time_per_rule
    
    assert "Average Confidence:" in metrics.pretty_print()
    assert "Density:" in metrics.summary()


def test_boundary_cache_stats():
    cache = BoundaryCache()
    cache.clear()
    
    doc_id = "test_doc_version"
    sem_hash = "abc123semantic"
    class_version = "v1.0"
    
    mock_boundaries = ["boundary_1", "boundary_2"]
    
    # Miss
    assert cache.get(doc_id, sem_hash, class_version) is None
    assert cache.cache_misses == 1
    assert cache.cache_hits == 0
    assert cache.hit_ratio == 0.0
    
    # Put and Get (Hit)
    cache.set(doc_id, sem_hash, class_version, mock_boundaries)
    assert cache.get(doc_id, sem_hash, class_version) == mock_boundaries
    assert cache.cache_hits == 1
    assert cache.hit_ratio == 0.50
    assert cache.average_lookup_time >= 0.0


def test_boundary_graph_navigation_and_exports():
    unit_a = SemanticUnit(
        id=uuid.uuid4(),
        structure_node_id=uuid.uuid4(),
        semantic_type="paragraph",
        content="Unit A",
        page_start=1,
        page_end=1,
        line_start=1,
        line_end=1,
        char_start=0,
        char_end=6
    )
    unit_b = SemanticUnit(
        id=uuid.uuid4(),
        structure_node_id=uuid.uuid4(),
        semantic_type="paragraph",
        content="Unit B",
        page_start=1,
        page_end=1,
        line_start=2,
        line_end=2,
        char_start=8,
        char_end=14
    )
    
    detector = SemanticBoundaryDetector()
    boundaries = detector.detect_boundaries([unit_a, unit_b])
    
    graph = BoundaryGraph([unit_a, unit_b], boundaries)
    
    # Navigation checks
    prev_b = graph.previous(unit_b)
    next_b = graph.next(unit_a)
    
    assert prev_b is not None
    assert next_b is not None
    assert prev_b.id == next_b.id
    
    # Graph visualization exports
    mermaid = graph.export_mermaid()
    assert "graph TD" in mermaid
    
    gv = graph.export_graphviz()
    assert "digraph G" in gv
    
    js = graph.export_json()
    assert "boundaries" in js

    # Explainability report validation (10.2C)
    report = graph.generate_explanation_report()
    assert len(report.items) == 2
    assert "Boundary Explanation Report" in report.to_markdown()
    assert "ID:" in report.pretty_print()
    assert isinstance(report.to_json(), str)


def test_semantic_boundary_validator():
    unit_a = SemanticUnit(
        id=uuid.uuid4(),
        structure_node_id=uuid.uuid4(),
        semantic_type="paragraph",
        content="Unit A",
        char_start=0,
        char_end=6
    )
    unit_b = SemanticUnit(
        id=uuid.uuid4(),
        structure_node_id=uuid.uuid4(),
        semantic_type="paragraph",
        content="Unit B",
        char_start=8,
        char_end=14
    )
    
    detector = SemanticBoundaryDetector()
    boundaries = detector.detect_boundaries([unit_a, unit_b])
    
    report = SemanticBoundaryValidator.validate([unit_a, unit_b], boundaries)
    assert report.is_valid

    unit_orphan = SemanticUnit(
        id=uuid.uuid4(),
        structure_node_id=uuid.uuid4(),
        semantic_type="paragraph",
        content="Unit Orphan",
        char_start=16,
        char_end=27
    )
    report_orphan = SemanticBoundaryValidator.validate([unit_a, unit_b, unit_orphan], boundaries)
    assert not report_orphan.is_valid

    boundaries[1].char_offset = -5
    report_order = SemanticBoundaryValidator.validate([unit_a, unit_b], boundaries)
    assert not report_order.is_valid


# ---------------------------------------------------------------------------
# NEW TEST CASES FOR PHASE 10.2C/REVISION
# ---------------------------------------------------------------------------

def test_boundary_replay_player():
    b1 = "boundary_1"
    b2 = "boundary_2"
    player = BoundaryReplayPlayer([b1, b2])
    
    assert player.current() == b1
    assert player.next() == b2
    assert player.current() == b2
    assert player.previous() == b1
    assert player.jump(1) == b2


class MockCustomPredictor(BaseBoundaryPredictor):
    def predict_boundaries(self, units, context=None):
        return [
            SemanticBoundary(
                id=uuid.uuid4(),
                previous_unit_id=units[0].id if units else None,
                next_unit_id=None,
                page=1,
                line=1,
                char_offset=0,
                boundary_type="CUSTOM_BREAK",
                final_confidence=0.99,
                importance_score=0.95
            )
        ]

def test_predictor_interface_and_di():
    # Test Dependency Injection
    custom_predictor = MockCustomPredictor()
    detector = SemanticBoundaryDetector(predictor=custom_predictor)
    
    units = [SemanticUnit(id=uuid.uuid4(), structure_node_id=uuid.uuid4(), semantic_type="paragraph", content="Para")]
    boundaries = detector.detect_boundaries(units)
    assert len(boundaries) == 1
    assert boundaries[0].boundary_type == "CUSTOM_BREAK"
    assert boundaries[0].final_confidence == 0.99


def test_boundary_identity_lineage_quality_hints():
    unit_a = SemanticUnit(
        id=uuid.uuid4(),
        structure_node_id=uuid.uuid4(),
        semantic_type="paragraph",
        content="This is standard text.",
        importance_score=0.50
    )
    unit_b = SemanticUnit(
        id=uuid.uuid4(),
        structure_node_id=uuid.uuid4(),
        semantic_type="code",
        content="print('Hello World')",
        importance_score=0.80,
        metadata={"keywords": ["python", "hello"]}
    )
    
    detector = SemanticBoundaryDetector()
    boundaries = detector.detect_boundaries([unit_a, unit_b])
    
    assert len(boundaries) == 2
    b = boundaries[0]
    
    # Boundary Identity
    assert b.boundary_hash != ""
    assert b.boundary_signature.startswith("sig_")
    assert b.boundary_version == "1.0"
    
    # Boundary Lineage
    assert "code_start" in b.generated_from_rules
    assert str(unit_a.structure_node_id) in b.generated_from_nodes
    
    # Boundary Quality
    assert 0.0 <= b.quality_score <= 1.0
    assert "confidence_contribution" in b.quality_breakdown
    
    # Retrieval Hints & Recommendations
    assert b.retrieval_hints["contains_code"] is True
    assert b.chunk_recommendation == "split"
