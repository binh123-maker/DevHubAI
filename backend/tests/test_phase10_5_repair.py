import uuid
import pytest
from app.services.chunking.semantic_chunk import SemanticChunk
from app.services.validation.semantic_validation_profile import SemanticValidationProfile
from app.services.validation.semantic_validator import SemanticValidator
from app.services.validation.semantic_repair_profile import SemanticRepairProfile
from app.services.validation.semantic_repair_result import SemanticRepairResult
from app.services.validation.semantic_repair_engine import SemanticRepairEngine
from app.services.validation.repair_rules import (
    SentenceRepairRule,
    CodeRepairRule,
    TableRepairRule,
    FormulaRepairRule,
    MetadataRepairRule,
    RetrievalRepairRule,
    ScoreRepairRule
)
from app.services.validation.repair_strategy import BalancedRepairStrategy, AggressiveRepairStrategy
from app.services.validation.repair_pipeline_context import RepairPipelineContext
from app.services.validation.repair_explanation_report import RepairExplanationReport
from app.services.validation.repair_graph import RepairGraph
from app.services.validation.repair_replay_player import RepairReplayPlayer
from app.services.validation.repair_cache import RepairCache

def test_repair_engine_and_rules():
    # 1. Chunk with multiple defects
    chunk = SemanticChunk(
        id=uuid.uuid4(),
        document_version_id=uuid.uuid4(),
        workspace_id=None,
        chunk_index=0,
        semantic_units=[],
        semantic_boundaries=[],
        content="```python\ndef run_test():\n  print('Hello')\nThis sentence has no period",
        language="en",
        heading_path=["Header"],
        section_path=["Section"],
        document_path=[],
        fingerprint="fp_repair_test_1"
    )
    
    # Validation before repair
    profile = SemanticValidationProfile()
    res = SemanticValidator.validate_chunk(chunk, profile)
    assert not res.overall_status == "VALID"
    
    # 2. Repair Engine with DI rules
    engine = SemanticRepairEngine(
        strategy=BalancedRepairStrategy(),
        rules=[SentenceRepairRule(), CodeRepairRule()]
    )
    
    repair_res = engine.repair_chunks([chunk], res)
    assert repair_res.repair_score > 0.0
    assert len(repair_res.repaired_issues) == 2
    
    # Check that code block and sentence ending are resolved
    assert "period." in chunk.content
    assert chunk.content.endswith("```")

    # 3. Strategy Switching & Context
    context = RepairPipelineContext(
        profile=SemanticRepairProfile(),
        strategy=AggressiveRepairStrategy(),
        validation_result=res
    )
    assert context.strategy.name == "AGGRESSIVE"

    # 4. Repair Graph, Timeline, Report, and Cache
    graph = RepairGraph(repair_res)
    assert "graph TD" in graph.export_mermaid()
    assert "digraph G" in graph.export_graphviz()
    assert isinstance(graph.export_json(), str)
    
    report = RepairExplanationReport(repair_res)
    assert "repaired_issues" in report.to_json()
    assert "Automatic Semantic Repair" in report.to_markdown()
    assert "Repair Score" in report.to_html()
    assert "=== Repair Results ===" in report.pretty_print()

    player = RepairReplayPlayer(repair_res)
    assert len(player.timeline()) == 2
    assert player.current().repair_type == "SentenceRepair"
    player.play()
    
    # Cache Check
    cache = RepairCache()
    cache.clear()
    assert cache.get("fp_none", "1.0") is None
    cache.set("fp_mock", "1.0", repair_res)
    assert cache.get("fp_mock", "1.0").repair_score == repair_res.repair_score
