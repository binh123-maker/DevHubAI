import uuid
from pathlib import Path
from app.services.document_structure.node_types import NodeType
from app.services.document_structure.document_structure_analyzer import analyze_document_structure

def test_structure_metadata_enrichment():
    # 1. Mock Markdown file with heading and paragraph containing code/table symbols
    content = (
        "# Parent Topic\n"
        "Here is a small paragraph with code block like `print(x)`. It has two sentences.\n"
    )
    temp_file = Path("test_metadata.md")
    temp_file.write_text(content, encoding="utf-8")
    
    try:
        nodes = analyze_document_structure(uuid.uuid4(), temp_file, "md")
        assert len(nodes) == 2
        
        # Verify paragraph metadata
        para = nodes[1]
        assert para["node_type"] == NodeType.PARAGRAPH.value
        
        metadata = para["metadata_json"]
        assert metadata["word_count"] > 0
        assert metadata["token_estimate"] > 0
        assert metadata["sentence_count"] == 2
        assert metadata["paragraph_count"] == 1
        assert "reading_time" in metadata
        
        # Path resolution
        assert metadata["heading_path"] == ["Parent Topic"]
        assert metadata["section_path"] == ["Parent Topic"]
        assert metadata["document_path"] == ["Parent Topic"]
        
        # Boolean tags
        assert metadata["contains_code"] is True
        assert metadata["contains_table"] is False
        assert metadata["contains_image"] is False
        
    finally:
        temp_file.unlink(missing_ok=True)
