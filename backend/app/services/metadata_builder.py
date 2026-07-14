import re
from typing import Any

def extract_code_metadata(content: str, language: str | None) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    
    # 1. Framework/Library detection
    frameworks = []
    if "fastapi" in content.lower() or "apirouter" in content:
        frameworks.append("FastAPI")
    if "spring" in content.lower() or "springboot" in content.lower():
        frameworks.append("Spring Boot")
    if "react" in content.lower() or "usestate" in content.lower():
        frameworks.append("React")
    if frameworks:
        metadata["frameworks"] = frameworks

    # 2. Imports/Exports extraction
    imports = []
    for m in re.finditer(r'^(?:import\s+(.+)|from\s+(\S+)\s+import\s+(.+))', content, re.MULTILINE):
        if m.group(1):
            imports.append(m.group(1).strip())
        elif m.group(2):
            imports.append(f"{m.group(2)}.{m.group(3)}")
    if imports:
        metadata["imports"] = imports

    # 3. Classes extraction
    classes = [m.group(1) for m in re.finditer(r'(?:class|struct|interface|enum)\s+(\w+)', content)]
    if classes:
        metadata["classes"] = classes

    # 4. Functions/Methods extraction
    functions = [m.group(1) for m in re.finditer(r'(?:def|function|fn)\s+(\w+)', content)]
    # Java/Spring style functions
    functions.extend([m.group(2) for m in re.finditer(r'(public|private|protected)\s+\w+\s+(\w+)\s*\(', content)])
    if functions:
        metadata["functions"] = functions

    # 5. Routes extraction (FastAPI, Spring Boot, Express style)
    routes = []
    for m in re.finditer(r'@(?:app|router|Get|Post|Put|Delete|RequestMapping|GetMapping|PostMapping)\((?:"|\')([^"\')]+)', content):
        routes.append(m.group(1))
    # Express style routes: app.get('/path', ...)
    for m in re.finditer(r'\.(?:get|post|put|delete)\(\s*(?:"|\')([^"\')]+)', content):
        routes.append(m.group(1))
    if routes:
        metadata["routes"] = routes

    # 6. Database Tables extraction
    tables = [m.group(1) for m in re.finditer(r'__tablename__\s*=\s*(?:"|\')([^"\')]+)', content)]
    # SQL queries: FROM table_name or JOIN table_name
    tables.extend([m.group(1) for m in re.finditer(r'(?:from|join|update|into)\s+(\w+)', content, re.IGNORECASE)])
    if tables:
        metadata["database_tables"] = list(set(tables))

    return metadata


def extract_text_metadata(content: str) -> dict[str, Any]:
    # Extract simple keywords (words > 4 chars, occurring in text, excluding common words)
    words = re.findall(r'\b\w{5,}\b', content.lower())
    stop_words = {"about", "there", "their", "would", "other", "which", "these", "where"}
    keywords = list(set([w for w in words if w not in stop_words]))[:10]
    
    return {"keywords": keywords}


def build_metadata(content: str, is_code: bool, language: str | None = None) -> dict[str, Any]:
    if is_code or language:
        return extract_code_metadata(content, language)
    return extract_text_metadata(content)
