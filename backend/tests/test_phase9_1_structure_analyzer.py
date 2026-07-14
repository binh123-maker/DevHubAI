import uuid
import pytest
from pathlib import Path

from app.services.document_structure.node_types import NodeType
from app.services.document_structure.document_structure_analyzer import analyze_document_structure
from app.services.document_structure.tree_validator import validate_tree, TreeValidationError

def test_markdown_structure_analysis():
    # 1. Mock Markdown file content
    content = (
        "# Heading 1\n"
        "Some paragraph here.\n"
        "## Heading 2\n"
        "- Bullet item 1\n"
        "1. Numbered item 1\n"
        "```python\n"
        "print('hello')\n"
        "```\n"
        "| header 1 | header 2 |\n"
        "|---|---|\n"
        "| val 1 | val 2 |\n"
    )
    temp_file = Path("test_structure.md")
    temp_file.write_text(content, encoding="utf-8")
    
    try:
        nodes = analyze_document_structure(uuid.uuid4(), temp_file, "md")
        assert len(nodes) > 0
        
        # Verify node types are extracted
        node_types = [n["node_type"] for n in nodes]
        assert NodeType.HEADING_1.value in node_types
        assert NodeType.HEADING_2.value in node_types
        assert NodeType.PARAGRAPH.value in node_types
        assert NodeType.BULLET_LIST.value in node_types
        assert NodeType.NUMBERED_LIST.value in node_types
        assert NodeType.CODE_BLOCK.value in node_types
        assert NodeType.TABLE.value in node_types
    finally:
        temp_file.unlink(missing_ok=True)


def test_txt_structure_analysis():
    content = (
        "SECTION ONE\n\n"
        "This is paragraph one.\n\n"
        "This is paragraph two."
    )
    temp_file = Path("test_structure.txt")
    temp_file.write_text(content, encoding="utf-8")
    try:
        nodes = analyze_document_structure(uuid.uuid4(), temp_file, "txt")
        assert len(nodes) == 3
        assert nodes[0]["node_type"] == NodeType.HEADING_1.value
        assert nodes[1]["node_type"] == NodeType.PARAGRAPH.value
        assert nodes[2]["node_type"] == NodeType.PARAGRAPH.value
    finally:
        temp_file.unlink(missing_ok=True)


def test_html_structure_analysis():
    content = (
        "<html><body>"
        "<h1>Title</h1>"
        "<p>Paragraph</p>"
        "<pre>code content</pre>"
        "<table><tr><td>Cell</td></tr></table>"
        "</body></html>"
    )
    temp_file = Path("test_structure.html")
    temp_file.write_text(content, encoding="utf-8")
    try:
        nodes = analyze_document_structure(uuid.uuid4(), temp_file, "html")
        node_types = [n["node_type"] for n in nodes]
        assert NodeType.HEADING_1.value in node_types
        assert NodeType.PARAGRAPH.value in node_types
        assert NodeType.CODE_BLOCK.value in node_types
        assert NodeType.TABLE.value in node_types
    finally:
        temp_file.unlink(missing_ok=True)


def test_tree_validation_rules():
    # 1. Test missing parent ID
    bad_nodes_parent = [
        {"id": uuid.uuid4(), "parent_id": uuid.uuid4(), "order_index": 0}
    ]
    with pytest.raises(TreeValidationError, match="references a missing parent_id"):
        validate_tree(bad_nodes_parent)

    # 2. Test invalid page range
    bad_nodes_pages = [
        {"id": uuid.uuid4(), "parent_id": None, "order_index": 0, "page_start": 5, "page_end": 2}
    ]
    with pytest.raises(TreeValidationError, match="invalid page range"):
        validate_tree(bad_nodes_pages)

    # 3. Test cycle reference
    n1 = uuid.uuid4()
    n2 = uuid.uuid4()
    bad_nodes_cycle = [
        {"id": n1, "parent_id": n2, "order_index": 0},
        {"id": n2, "parent_id": n1, "order_index": 1}
    ]
    with pytest.raises(TreeValidationError, match="Circular reference detected"):
        validate_tree(bad_nodes_cycle)

    # 4. Test duplicate/non-contiguous ordering
    bad_nodes_order = [
        {"id": uuid.uuid4(), "parent_id": None, "order_index": 0},
        {"id": uuid.uuid4(), "parent_id": None, "order_index": 2}
    ]
    with pytest.raises(TreeValidationError, match="Order indices are not contiguous"):
        validate_tree(bad_nodes_order)
