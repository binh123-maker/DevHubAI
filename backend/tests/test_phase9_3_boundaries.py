import uuid
import pytest
from pathlib import Path
from app.services.document_structure.node_types import NodeType
from app.services.document_structure.document_structure_analyzer import analyze_document_structure
from app.services.document_structure.tree_validator import validate_tree, TreeValidationError

def test_non_heading_section_boundaries():
    # 1. Mock Markdown file with lists, code block, and tables
    content = (
        "- Bullet Item 1\n"
        "- Bullet Item 2\n"
        "```python\n"
        "print('hello')\n"
        "```\n"
        "| a | b |\n"
        "|---|---|\n"
        "| 1 | 2 |\n"
    )
    temp_file = Path("test_boundaries.md")
    temp_file.write_text(content, encoding="utf-8")
    
    try:
        nodes = analyze_document_structure(uuid.uuid4(), temp_file, "md")
        assert len(nodes) > 0
        
        # Verify first two list items share the exact same section boundary
        item1 = nodes[0]
        item2 = nodes[1]
        assert item1["node_type"] == NodeType.BULLET_LIST.value
        assert item2["node_type"] == NodeType.BULLET_LIST.value
        
        bound1 = item1["metadata_json"]["section_boundary"]
        bound2 = item2["metadata_json"]["section_boundary"]
        assert bound1 == bound2
        assert bound1["char_start"] == item1["char_start"]
        assert bound1["char_end"] == item2["char_end"]
        
        # Verify code block boundary matches itself
        code_node = nodes[2]
        assert code_node["node_type"] == NodeType.CODE_BLOCK.value
        code_bound = code_node["metadata_json"]["section_boundary"]
        assert code_bound["char_start"] == code_node["char_start"]
        assert code_bound["char_end"] == code_node["char_end"]
        
        # Verify table boundary matches itself
        table_node = nodes[3]
        assert table_node["node_type"] == NodeType.TABLE.value
        table_bound = table_node["metadata_json"]["section_boundary"]
        assert table_bound["char_start"] == table_node["char_start"]
        assert table_bound["char_end"] == table_node["char_end"]
        
    finally:
        temp_file.unlink(missing_ok=True)


def test_invalid_boundary_validation():
    # Test validator throws for invalid b_char_start > b_char_end
    bad_nodes = [
        {
            "id": uuid.uuid4(),
            "parent_id": None,
            "order_index": 0,
            "page_start": 1,
            "page_end": 1,
            "metadata_json": {
                "section_boundary": {
                    "char_start": 50,
                    "char_end": 20,
                    "line_start": 1,
                    "line_end": 2,
                    "page_start": 1,
                    "page_end": 1
                }
            }
        }
    ]
    with pytest.raises(TreeValidationError, match="invalid section boundary characters range"):
        validate_tree(bad_nodes)
