import uuid
import pytest
from typing import List, Any, Optional

from app.services.semantic.semantic_unit import SemanticUnit
from app.services.semantic.semantic_boundary import SemanticBoundary
from app.services.chunking.semantic_chunk import SemanticChunk
from app.services.chunking.base_chunk_builder import BaseChunkBuilder
from app.services.chunking.rule_based_chunk_builder import RuleBasedChunkBuilder
from app.services.chunking.chunk_optimizer import ChunkOptimizer
from app.services.chunking.chunk_pipeline_context import ChunkPipelineContext
from app.services.chunking.chunk_builder_config import ChunkBuilderConfiguration
from app.services.chunking.chunk_statistics import ChunkStatistics
from app.services.chunking.chunk_validator import ChunkValidator
from app.services.chunking.chunk_graph import ChunkGraph
from app.services.chunking.chunk_replay_player import ChunkReplayPlayer
from app.services.chunking.chunk_cache import ChunkCache
from app.services.chunking.chunk_metrics import ChunkMetrics
from app.services.chunking.chunk_explanation_report import ChunkExplanationReport
from app.services.chunking.semantic_chunk_builder import SemanticChunkBuilder
from app.services.chunking.chunk_intelligence import ChunkIntelligenceAnalyzer
from app.services.chunking.chunk_events import ChunkOptimized, ChunkCacheHit, ChunkPipelineFinished

# Dummy mock builder for DI tests
class MockDIBuilder(BaseChunkBuilder):
    def build_chunks(self, units: List[Any], boundaries: List[Any], context: Optional[Any] = None) -> List[Any]:
        # Return mock semantic chunks
        return [
            SemanticChunk(
                id=uuid.uuid4(),
                document_version_id=uuid.uuid4(),
                workspace_id=None,
                chunk_index=0,
                semantic_units=[],
                semantic_boundaries=[],
                content="Mock DI chunk content",
                language="en",
                heading_path=["DI Heading"],
                section_path=["DI Section"],
                document_path=[]
            )
        ]
    def merge_chunks(self, chunks: List[Any], context: Optional[Any] = None) -> List[Any]:
        return chunks
    def split_chunks(self, chunks: List[Any], context: Optional[Any] = None) -> List[Any]:
        return chunks
    def optimize_chunks(self, chunks: List[Any], context: Optional[Any] = None) -> List[Any]:
        return chunks
    def validate_chunks(self, chunks: List[Any], context: Optional[Any] = None) -> Any:
        return None
    def supports(self, document_type: str) -> bool:
        return document_type == "di_mock"


def test_semantic_chunk_builder_basic_and_splits():
    doc_node_1 = uuid.uuid4()
    doc_node_2 = uuid.uuid4()
    
    units = [
        SemanticUnit(
            id=uuid.uuid4(),
            structure_node_id=doc_node_1,
            semantic_type="paragraph",
            content="This is the first sentence under heading one.",
            heading_path=["Chapter 1"],
            section_path=["Chapter 1", "Section 1"],
            language="en",
            importance_score=0.70
        ),
        SemanticUnit(
            id=uuid.uuid4(),
            structure_node_id=doc_node_1,
            semantic_type="paragraph",
            content="This is the second sentence under heading one.",
            heading_path=["Chapter 1"],
            section_path=["Chapter 1", "Section 1"],
            language="en",
            importance_score=0.60
        ),
        SemanticUnit(
            id=uuid.uuid4(),
            structure_node_id=doc_node_2,
            semantic_type="paragraph",
            content="This is a sentence under a new heading two.",
            heading_path=["Chapter 2"],
            section_path=["Chapter 2", "Section 1"],
            language="en",
            importance_score=0.85
        )
    ]
    
    boundary_1 = SemanticBoundary(
        id=uuid.uuid4(),
        previous_unit_id=units[0].id,
        next_unit_id=units[1].id,
        page=1,
        line=2,
        char_offset=44,
        boundary_type="HEADING_BREAK",
        final_confidence=0.90,
        quality_score=0.85,
        chunk_recommendation="split"
    )
    
    boundary_2 = SemanticBoundary(
        id=uuid.uuid4(),
        previous_unit_id=units[1].id,
        next_unit_id=units[2].id,
        page=1,
        line=4,
        char_offset=90,
        boundary_type="HEADING_BREAK",
        final_confidence=0.95,
        quality_score=0.90,
        chunk_recommendation="split"
    )
    
    builder = SemanticChunkBuilder()
    chunks = builder.build_chunks(units, [boundary_1, boundary_2])

    assert len(chunks) == 3
    assert chunks[0].estimated_tokens > 0
    assert chunks[0].content == "This is the first sentence under heading one."
    assert chunks[1].content == "This is the second sentence under heading one."
    assert chunks[2].content == "This is a sentence under a new heading two."


def test_merge_small_chunks_and_overlap():
    units = [
        SemanticUnit(
            id=uuid.uuid4(),
            structure_node_id=uuid.uuid4(),
            semantic_type="paragraph",
            content="Short 1.",
            heading_path=["Chapter 1"],
            section_path=["Chapter 1"],
            language="en",
            importance_score=0.5
        ),
        SemanticUnit(
            id=uuid.uuid4(),
            structure_node_id=uuid.uuid4(),
            semantic_type="paragraph",
            content="Short 2.",
            heading_path=["Chapter 1"],
            section_path=["Chapter 1"],
            language="en",
            importance_score=0.6
        )
    ]
    
    boundary = SemanticBoundary(
        id=uuid.uuid4(),
        previous_unit_id=units[0].id,
        next_unit_id=units[1].id,
        page=1,
        line=1,
        char_offset=8,
        boundary_type="FALLBACK_BOUNDARY",
        final_confidence=0.20,
        quality_score=0.50,
        chunk_recommendation="merge"
    )
    
    config = ChunkBuilderConfiguration(
        default_min_tokens=100,
        enable_merge_small_chunks=True,
        enable_overlap=True,
        max_overlap=20
    )
    builder = SemanticChunkBuilder(config=config)
    chunks = builder.build_chunks(units, [boundary])
    
    assert len(chunks) == 1
    assert chunks[0].content == "Short 1. Short 2."


def test_split_large_chunks_and_overlap_generation():
    units = [
        SemanticUnit(
            id=uuid.uuid4(),
            structure_node_id=uuid.uuid4(),
            semantic_type="paragraph",
            content="This is standard paragraph text that is relatively long.",
            heading_path=["Chapter 1"],
            section_path=["Chapter 1"],
            language="en",
            importance_score=0.5
        ),
        SemanticUnit(
            id=uuid.uuid4(),
            structure_node_id=uuid.uuid4(),
            semantic_type="paragraph",
            content="This is another paragraph to add length.",
            heading_path=["Chapter 1"],
            section_path=["Chapter 1"],
            language="en",
            importance_score=0.5
        )
    ]
    
    boundary = SemanticBoundary(
        id=uuid.uuid4(),
        previous_unit_id=units[0].id,
        next_unit_id=units[1].id,
        page=1,
        line=1,
        char_offset=56,
        boundary_type="FALLBACK_BOUNDARY",
        final_confidence=0.20,
        quality_score=0.50,
        chunk_recommendation="preserve"
    )
    
    config = ChunkBuilderConfiguration(
        default_max_tokens=5,
        enable_split_large_chunks=True,
        enable_overlap=True,
        max_overlap=15
    )
    builder = SemanticChunkBuilder(config=config)
    chunks = builder.build_chunks(units, [boundary])
    
    assert len(chunks) == 2


def test_chunk_graph_navigation_and_replay():
    units = [
        SemanticUnit(id=uuid.uuid4(), structure_node_id=uuid.uuid4(), semantic_type="paragraph", content="Unit 1", heading_path=["H1"], section_path=["S1"]),
        SemanticUnit(id=uuid.uuid4(), structure_node_id=uuid.uuid4(), semantic_type="paragraph", content="Unit 2", heading_path=["H2"], section_path=["S2"])
    ]
    
    config = ChunkBuilderConfiguration(enable_merge_small_chunks=False)
    builder = SemanticChunkBuilder(config=config)
    chunks = builder.build_chunks(units, [])
    
    graph = ChunkGraph(chunks)
    
    assert graph.previous(chunks[1]).id == chunks[0].id
    assert graph.next(chunks[0]).id == chunks[1].id
    assert graph.find_previous(chunks[1]).id == chunks[0].id
    assert graph.find_next(chunks[0]).id == chunks[1].id
    assert len(graph.find_path(chunks[0].id, chunks[1].id)) == 2
    assert "nodes" in graph.find_subgraph([chunks[0].id])
    
    assert "graph TD" in graph.export_mermaid()
    assert "digraph G" in graph.export_graphviz()
    assert "chunks" in graph.export_json()

    player = ChunkReplayPlayer(chunks)
    assert player.length() == 2
    assert player.current().id == chunks[0].id
    player.play()
    assert len(player.timeline()) == 2


def test_chunk_validator_and_reports():
    units = [
        SemanticUnit(id=uuid.uuid4(), structure_node_id=uuid.uuid4(), semantic_type="paragraph", content="Unit 1")
    ]
    builder = SemanticChunkBuilder()
    chunks = builder.build_chunks(units, [])
    
    report = ChunkValidator.validate(chunks, units)
    assert report.is_valid
    assert "VALID" in report.summary()
    assert "Status: VALID" in report.pretty_print()


def test_chunk_cache_and_explanation():
    cache = ChunkCache()
    cache.clear()
    
    doc_id = "test_doc"
    sem_hash = "abc123semantic"
    
    assert cache.get(doc_id, sem_hash) is None
    cache.set(doc_id, sem_hash, ["chunk_1"])
    assert cache.get(doc_id, sem_hash) == ["chunk_1"]
    
    stats = cache.statistics()
    assert stats["cache_hits"] == 1
    assert stats["hit_ratio"] == 0.5

    report_items = [{
        "id": "chunk_id",
        "chunk_signature": "SIG_1",
        "creation_reason": "test creation",
        "merge_reason": "none",
        "split_reason": "none",
        "quality_score": 0.85,
        "retrieval_weight": 0.90,
        "importance_score": 0.80,
        "heading_path": ["Chapter 1"],
        "dominant_type": "TEXT",
        "recommended_search_modes": ["SEMANTIC"],
        "quality_breakdown": {}
    }]
    report = ChunkExplanationReport(report_items)
    assert "Chapter 1" in report.to_markdown()
    assert "chunk_id" in report.pretty_print()


def test_chunk_intelligence_analyzer():
    assert ChunkIntelligenceAnalyzer.calculate_heading_relevance(["Chapter One"], "Welcome to Chapter One text.") == 1.0
    
    units = [
        SemanticUnit(id=uuid.uuid4(), structure_node_id=uuid.uuid4(), semantic_type="code", content="def test(): pass"),
        SemanticUnit(id=uuid.uuid4(), structure_node_id=uuid.uuid4(), semantic_type="paragraph", content="Regular text.")
    ]
    assert ChunkIntelligenceAnalyzer.calculate_code_density(units) > 0.0
    assert ChunkIntelligenceAnalyzer.detect_chunk_type(units) == "CODE"


# ---------------------------------------------------------------------------
# PHASE 10.3D PRODUCTION INFRASTRUCTURE UNIT TESTS
# ---------------------------------------------------------------------------

def test_production_dependency_injection_and_context():
    # Setup context, config and DI mock builder
    config = ChunkBuilderConfiguration()
    context = ChunkPipelineContext(document_version_id=uuid.uuid4(), workspace_id=uuid.uuid4(), config=config)
    mock_builder = MockDIBuilder()

    # Injects mock builder into standard orchestrator SemanticChunkBuilder
    orchestrator = SemanticChunkBuilder(builder=mock_builder, config=config, context=context)
    
    units = [
        SemanticUnit(id=uuid.uuid4(), structure_node_id=uuid.uuid4(), semantic_type="paragraph", content="Test DI")
    ]
    chunks = orchestrator.build_chunks(units, [])
    
    assert len(chunks) == 1
    assert chunks[0].content == "Mock DI chunk content"
    assert orchestrator.builder.supports("di_mock") is True

    # Validate timings, metrics and optimizer outputs
    assert orchestrator.metrics.average_chunk_build_time >= 0.0
    assert orchestrator.metrics.average_optimizer_time >= 0.0
    assert context.validation is not None


def test_optimizer_and_events():
    # Verify optimizer overrides properties and strips self-redundant overlaps
    optimizer = ChunkOptimizer()
    
    chunk = SemanticChunk(
        id=uuid.uuid4(),
        document_version_id=uuid.uuid4(),
        workspace_id=None,
        chunk_index=0,
        semantic_units=[],
        semantic_boundaries=[],
        content="This is overlap content.",
        language="en",
        heading_path=["Header"],
        section_path=["Section"],
        document_path=[],
        overlap_before="This is overlap content.",
        quality_breakdown={"heading_relevance": 0.9}
    )

    optimized_chunks, report = optimizer.optimize_chunks([chunk])
    assert optimized_chunks[0].overlap_before == "" # stripped since it's identical to content
    assert report["redundant_overlaps_removed"] == 1

    # Verify event structures
    evt = ChunkOptimized(chunk.id, "Optimized overlaps")
    assert evt.event_type == "ChunkOptimized"
    assert evt.chunk_id == chunk.id
