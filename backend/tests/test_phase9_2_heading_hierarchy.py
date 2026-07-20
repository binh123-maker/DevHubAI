import uuid
from pathlib import Path
from app.services.document_structure.node_types import NodeType
from app.services.document_structure.document_structure_analyzer import analyze_document_structure

def test_heading_hierarchy_repair_and_metadata():
    # 1. Mock Markdown file with skipped heading level (H1 -> H2 -> H4)
    content = (
        "# First Heading\n"
        "Paragraph 1\n"
        "## Sub Heading\n"
        "Paragraph 2\n"
        "#### Skipped Heading\n"
        "Paragraph 3\n"
    )
    temp_file = Path("test_hierarchy.md")
    temp_file.write_text(content, encoding="utf-8")
    
    try:
        nodes = analyze_document_structure(uuid.uuid4(), temp_file, "md")
        assert len(nodes) > 0
        
        # Heading 1 (order 0)
        h1 = nodes[0]
        assert h1["node_type"] == NodeType.HEADING_1.value
        assert h1["hierarchy_level"] == 1
        assert h1["parent_id"] is None
        
        # Heading 2 (order 2)
        h2 = nodes[2]
        assert h2["node_type"] == NodeType.HEADING_2.value
        assert h2["hierarchy_level"] == 2
        assert h2["parent_id"] == h1["id"]
        
        # Heading 4 (order 4) - Repaired to level 3
        h4 = nodes[4]
        assert h4["node_type"] == NodeType.HEADING_4.value
        assert h4["hierarchy_level"] == 3
        assert h4["parent_id"] == h2["id"]
        
        # Sibling index checks
        # Paragraph 1 has sibling_index = 0 under h1
        # Heading 2 has sibling_index = 1 under h1
        assert nodes[1]["metadata_json"]["sibling_index"] == 0
        assert nodes[2]["metadata_json"]["sibling_index"] == 1
        
        # Section boundary checks
        h1_boundary = h1["metadata_json"]["section_boundary"]
        assert h1_boundary["char_start"] == h1["char_start"]
        assert h1_boundary["char_end"] >= nodes[-1]["char_end"]
        
    finally:
        temp_file.unlink(missing_ok=True)
