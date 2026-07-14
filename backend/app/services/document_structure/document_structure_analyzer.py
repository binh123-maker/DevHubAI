import logging
from pathlib import Path
from uuid import UUID
from bs4 import BeautifulSoup

from app.services.document_structure.node_types import NodeType
from app.services.document_structure.tree_builder import DocumentTreeBuilder
from app.services.document_structure.tree_validator import validate_tree

logger = logging.getLogger(__name__)

def analyze_document_structure(document_version_id: UUID, file_path: Path, file_type: str) -> list[dict]:
    """
    Main entrypoint to analyze a document version file, construct its logical tree,
    validate it, and return a flat list of node dictionary representations.
    """
    builder = DocumentTreeBuilder(document_version_id)
    ft = file_type.lower().strip(".")

    if ft == "md":
        content = ""
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            try:
                content = file_path.read_text(encoding="latin1")
            except Exception:
                pass
        _analyze_markdown(builder, content)

    elif ft == "pdf":
        _analyze_pdf(builder, file_path)

    elif ft == "docx":
        _analyze_docx(builder, file_path)

    elif ft == "txt":
        content = ""
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            try:
                content = file_path.read_text(encoding="latin-1")
            except Exception:
                pass
        _analyze_txt(builder, content)

    elif ft in ("html", "htm"):
        content = ""
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            pass
        _analyze_html(builder, content)

    else:
        # Fallback for other formats (e.g. unknown URL Resource / raw web response)
        content = ""
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            pass
        _analyze_markdown(builder, content)

    # Finalize structure properties
    nodes = builder.finalize()
    # Validate logical tree integrity
    validate_tree(nodes)
    return nodes


def _analyze_markdown(builder: DocumentTreeBuilder, content: str):
    lines = content.splitlines()
    char_offset = 0
    line_no = 1
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            char_offset += len(lines[i]) + 1
            line_no += 1
            i += 1
            continue

        # Code block
        if line.startswith("```"):
            lang = line[3:].strip() or None
            code_lines = []
            start_line = line_no
            start_char = char_offset
            char_offset += len(lines[i]) + 1
            line_no += 1
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                char_offset += len(lines[i]) + 1
                line_no += 1
                i += 1
            if i < len(lines):
                char_offset += len(lines[i]) + 1
                line_no += 1
                i += 1
            inner_code = "\n".join(code_lines)
            builder.add_node(
                node_type=NodeType.CODE_BLOCK,
                node_category="code",
                content_text=inner_code,
                content_markdown=f"```{lang or ''}\n{inner_code}\n```",
                page_start=1,
                page_end=1,
                char_start=start_char,
                char_end=char_offset,
                line_start=start_line,
                line_end=line_no - 1,
                language=lang
            )
            continue

        # Heading
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            text = line.lstrip("#").strip()
            node_type = NodeType.HEADING_1
            if level == 2:
                node_type = NodeType.HEADING_2
            elif level >= 3:
                node_type = NodeType.HEADING_3
            builder.add_node(
                node_type=node_type,
                node_category="heading",
                content_text=text,
                content_markdown=line,
                page_start=1,
                page_end=1,
                char_start=char_offset,
                char_end=char_offset + len(lines[i]),
                line_start=line_no,
                line_end=line_no,
                hierarchy_level=level
            )
            char_offset += len(lines[i]) + 1
            line_no += 1
            i += 1
            continue

        # Bullet lists / numbered lists
        if line.startswith(("- ", "* ", "+ ")) or (line[0].isdigit() and ". " in line[:4]):
            node_type = NodeType.BULLET_LIST if line.startswith(("- ", "* ", "+ ")) else NodeType.NUMBERED_LIST
            text = line.split(" ", 1)[1] if " " in line else line
            builder.add_node(
                node_type=node_type,
                node_category="list",
                content_text=text,
                content_markdown=line,
                page_start=1,
                page_end=1,
                char_start=char_offset,
                char_end=char_offset + len(lines[i]),
                line_start=line_no,
                line_end=line_no
            )
            char_offset += len(lines[i]) + 1
            line_no += 1
            i += 1
            continue

        # Tables
        if line.startswith("|") and line.endswith("|"):
            builder.add_node(
                node_type=NodeType.TABLE,
                node_category="table",
                content_text=line,
                content_markdown=line,
                page_start=1,
                page_end=1,
                char_start=char_offset,
                char_end=char_offset + len(lines[i]),
                line_start=line_no,
                line_end=line_no
            )
            char_offset += len(lines[i]) + 1
            line_no += 1
            i += 1
            continue

        # Paragraph
        builder.add_node(
            node_type=NodeType.PARAGRAPH,
            node_category="text",
            content_text=line,
            content_markdown=line,
            page_start=1,
            page_end=1,
            char_start=char_offset,
            char_end=char_offset + len(lines[i]),
            line_start=line_no,
            line_end=line_no
        )
        char_offset += len(lines[i]) + 1
        line_no += 1
        i += 1


def _analyze_pdf(builder: DocumentTreeBuilder, file_path: Path):
    import fitz
    doc = fitz.open(str(file_path))
    char_offset = 0
    
    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("blocks")
        line_no = 1
        for block in blocks:
            text = block[4].strip()
            if not text:
                continue

            node_type = NodeType.PARAGRAPH
            # Crude header check
            if len(text) < 100 and (text.startswith("Chapter") or text.startswith("Section") or text.isupper()):
                node_type = NodeType.HEADING_1

            builder.add_node(
                node_type=node_type,
                node_category="content",
                content_text=text,
                content_markdown=text,
                page_start=page_num,
                page_end=page_num,
                char_start=char_offset,
                char_end=char_offset + len(text),
                line_start=line_no,
                line_end=line_no + text.count("\n"),
                hierarchy_level=1 if node_type == NodeType.HEADING_1 else 0
            )
            char_offset += len(text) + 1
            line_no += text.count("\n") + 1
    doc.close()


def _analyze_docx(builder: DocumentTreeBuilder, file_path: Path):
    try:
        import docx
        doc = docx.Document(str(file_path))
        char_offset = 0
        line_no = 1
        for p in doc.paragraphs:
            text = p.text.strip()
            if not text:
                continue

            node_type = NodeType.PARAGRAPH
            style_name = p.style.name.lower() if p.style else ""
            level = 0
            if "heading 1" in style_name:
                node_type = NodeType.HEADING_1
                level = 1
            elif "heading 2" in style_name:
                node_type = NodeType.HEADING_2
                level = 2
            elif "heading 3" in style_name:
                node_type = NodeType.HEADING_3
                level = 3
            elif "list" in style_name:
                node_type = NodeType.BULLET_LIST

            builder.add_node(
                node_type=node_type,
                node_category="content",
                content_text=text,
                content_markdown=text,
                page_start=1,
                page_end=1,
                char_start=char_offset,
                char_end=char_offset + len(text),
                line_start=line_no,
                line_end=line_no,
                hierarchy_level=level
            )
            char_offset += len(text) + 1
            line_no += 1
    except Exception:
        # Graceful basic DOCX parser fallback
        builder.add_node(
            node_type=NodeType.PARAGRAPH,
            node_category="text",
            content_text="[DOCX content placeholder]",
            content_markdown="[DOCX content placeholder]",
            page_start=1,
            page_end=1,
            char_start=0,
            char_end=25,
            line_start=1,
            line_end=1
        )


def _analyze_txt(builder: DocumentTreeBuilder, content: str):
    # Infer sections by splitting by blank lines
    blocks = content.split("\n\n")
    char_offset = 0
    line_no = 1
    for block in blocks:
        text = block.strip()
        if not text:
            continue

        node_type = NodeType.PARAGRAPH
        if len(text) < 80 and text.isupper():
            node_type = NodeType.HEADING_1

        builder.add_node(
            node_type=node_type,
            node_category="text",
            content_text=text,
            content_markdown=text,
            page_start=1,
            page_end=1,
            char_start=char_offset,
            char_end=char_offset + len(text),
            line_start=line_no,
            line_end=line_no + text.count("\n")
        )
        char_offset += len(block) + 2
        line_no += block.count("\n") + 2


def _analyze_html(builder: DocumentTreeBuilder, content: str):
    soup = BeautifulSoup(content, "html.parser")
    char_offset = 0
    line_no = 1

    # Extract logical structure from elements
    for el in soup.find_all(["h1", "h2", "h3", "p", "pre", "ul", "ol", "table"]):
        text = el.get_text().strip()
        if not text:
            continue

        node_type = NodeType.PARAGRAPH
        level = 0

        if el.name == "h1":
            node_type = NodeType.HEADING_1
            level = 1
        elif el.name == "h2":
            node_type = NodeType.HEADING_2
            level = 2
        elif el.name == "h3":
            node_type = NodeType.HEADING_3
            level = 3
        elif el.name in ("ul", "ol"):
            node_type = NodeType.BULLET_LIST if el.name == "ul" else NodeType.NUMBERED_LIST
        elif el.name == "pre":
            node_type = NodeType.CODE_BLOCK
        elif el.name == "table":
            node_type = NodeType.TABLE

        builder.add_node(
            node_type=node_type,
            node_category="html_element",
            content_text=text,
            content_markdown=text,
            page_start=1,
            page_end=1,
            char_start=char_offset,
            char_end=char_offset + len(text),
            line_start=line_no,
            line_end=line_no + text.count("\n"),
            hierarchy_level=level
        )
        char_offset += len(text) + 1
        line_no += text.count("\n") + 1
