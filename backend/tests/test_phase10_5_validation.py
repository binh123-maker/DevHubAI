import uuid
import pytest
from app.services.chunking.semantic_chunk import SemanticChunk
from app.services.validation.semantic_validation_profile import SemanticValidationProfile
from app.services.validation.validation_issue import ValidationIssue
from app.services.validation.semantic_validation_result import SemanticValidationResult
from app.services.validation.semantic_validator import SemanticValidator
from app.services.validation.validation_explanation_report import ValidationExplanationReport
from app.services.validation.validation_graph import ValidationGraph
from app.services.validation.validation_replay_player import ValidationReplayPlayer
from app.services.validation.validation_cache import ValidationCache

def test_structural_and_semantic_validation():
    # 1. Broken Sentence chunk
    chunk_sentence = SemanticChunk(
        id=uuid.uuid4(),
        document_version_id=uuid.uuid4(),
        workspace_id=None,
        chunk_index=0,
        semantic_units=[],
        semantic_boundaries=[],
        content="This ends without period",
        language="en",
        heading_path=["Header"],
        section_path=["Section"],
        document_path=[],
        fingerprint="fp_sentence"
    )
    res = SemanticValidator.validate_chunk(chunk_sentence)
    assert res.overall_validation_score < 1.0
    assert any(i.subcategory == "Broken Sentence" for i in res.issues)

    # 2. Broken Code chunk
    chunk_code = SemanticChunk(
        id=uuid.uuid4(),
        document_version_id=uuid.uuid4(),
        workspace_id=None,
        chunk_index=1,
        semantic_units=[],
        semantic_boundaries=[],
        content="```python\ndef test():",
        language="en",
        heading_path=["Header"],
        section_path=["Section"],
        document_path=[],
        fingerprint="fp_code"
    )
    res_code = SemanticValidator.validate_chunk(chunk_code)
    assert any(i.subcategory == "Broken Code" for i in res_code.issues)

    # 3. Broken Table chunk
    chunk_table = SemanticChunk(
        id=uuid.uuid4(),
        document_version_id=uuid.uuid4(),
        workspace_id=None,
        chunk_index=2,
        semantic_units=[],
        semantic_boundaries=[],
        content="| Col1 | Col2 |\n|---|---|\n| Row1 |",
        language="en",
        heading_path=["Header"],
        section_path=["Section"],
        document_path=[],
        fingerprint="fp_table"
    )
    res_table = SemanticValidator.validate_chunk(chunk_table)
    assert any(i.subcategory == "Broken Table" for i in res_table.issues)

    # 4. Broken Formula chunk
    chunk_formula = SemanticChunk(
        id=uuid.uuid4(),
        document_version_id=uuid.uuid4(),
        workspace_id=None,
        chunk_index=3,
        semantic_units=[],
        semantic_boundaries=[],
        content="Math mode $e=mc^2 is not closed.",
        language="en",
        heading_path=["Header"],
        section_path=["Section"],
        document_path=[],
        fingerprint="fp_formula"
    )
    res_formula = SemanticValidator.validate_chunk(chunk_formula)
    assert any(i.subcategory == "Broken Formula" for i in res_formula.issues)


def test_validation_reports_and_graph():
    chunk = SemanticChunk(
        id=uuid.uuid4(),
        document_version_id=uuid.uuid4(),
        workspace_id=None,
        chunk_index=0,
        semantic_units=[],
        semantic_boundaries=[],
        content="Invalid overlap code ```",
        language="en",
        heading_path=["Header"],
        section_path=["Section"],
        document_path=[],
        fingerprint="fp_report_graph"
    )
    res = SemanticValidator.validate_chunk(chunk)
    
    # Validation Explanation Report
    report = ValidationExplanationReport(res)
    assert "Detected Validation Issues" in report.to_markdown()
    assert isinstance(report.to_json(), str)
    assert "Validation Score:" in report.to_html()
    assert "Status: INVALID" in report.pretty_print()

    # Validation Graph Exporter
    graph = ValidationGraph(res)
    assert "graph TD" in graph.export_mermaid()
    assert "digraph G" in graph.export_graphviz()
    assert "nodes" in graph.export_json()
    assert graph.pipeline_health_graph()["type"] == "PipelineHealthGraph"


def test_validation_cache_and_player():
    cache = ValidationCache()
    cache.clear()

    fp = "chunk_fingerprint_abc"
    ver = "1.0"
    
    assert cache.get(fp, ver) is None
    
    score1 = ValidationIssue(
        severity="CRITICAL",
        category="Quality",
        subcategory="Low Quality",
        rule_name="ThresholdRule",
        affected_chunk=uuid.uuid4(),
        description="Bad",
        recommendation="None",
        repair_hint="None"
    )
    mock_res = SemanticValidationResult(overall_validation_score=0.8, issues=[score1])
    cache.set(fp, ver, mock_res)
    
    assert cache.get(fp, ver).overall_validation_score == 0.8
    stats = cache.statistics()
    assert stats["hits"] == 1
    assert stats["hit_ratio"] == 0.5

    # Replay Player
    player = ValidationReplayPlayer(mock_res)
    assert player.current().rule_name == "ThresholdRule"
    player.play()
    assert len(player.timeline()) == 1
