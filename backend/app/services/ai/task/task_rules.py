import re
from typing import List, Tuple
from app.services.ai.task.task_type import TaskType

# Deterministic regex and keyword rules for fast classification without LLM calls
TASK_KEYWORD_RULES: List[Tuple[TaskType, List[str], float]] = [
    (
        TaskType.SUMMARIZATION,
        [r"\bsummariz(e|ation)\b", r"\btl;?dr\b", r"\bbrief overview\b", r"\bkey takeaways\b", r"\bsummarise\b"],
        0.90
    ),
    (
        TaskType.CODE_EXPLANATION,
        [r"\bexplain (this|the) code\b", r"\bhow does this (code|function|script|class) work\b", r"\bcode explanation\b"],
        0.95
    ),
    (
        TaskType.CODE_REVIEW,
        [r"\breview (this|my) code\b", r"\bcode review\b", r"\brefactor (this|my) code\b", r"\bfind bugs in\b"],
        0.90
    ),
    (
        TaskType.CODE_GENERATION,
        [r"\bwrite (a|the) (code|script|function|class|program)\b", r"\bimplement a\b", r"\bgenerate code\b", r"\bcreate a function\b"],
        0.90
    ),
    (
        TaskType.REASONING,
        [r"\bstep[- ]by[- ]step\b", r"\bexplain your reasoning\b", r"\bprove that\b", r"\bsolve this math\b", r"\bthink through\b"],
        0.85
    ),
    (
        TaskType.TITLE_GENERATION,
        [r"\bgenerate (a|the) title\b", r"\bcreate a title\b", r"\bname this (chat|conversation|thread)\b"],
        0.95
    ),
    (
        TaskType.KEYWORD_EXTRACTION,
        [r"\bextract (keywords|key phrases|entities)\b", r"\bkeyword extraction\b"],
        0.95
    ),
    (
        TaskType.TAG_GENERATION,
        [r"\bgenerate tags\b", r"\bextract tags\b", r"\btag this\b"],
        0.95
    ),
    (
        TaskType.DOCUMENT_ANALYSIS,
        [r"\banalyze (this|the) document\b", r"\bextract metadata\b", r"\bparse document\b"],
        0.90
    ),
    (
        TaskType.EMBEDDING,
        [r"\bgenerate embedding\b", r"\bvectorize\b", r"\bembed text\b"],
        0.99
    ),
    (
        TaskType.CLASSIFICATION,
        [r"\bclassify (this|the)\b", r"\bcategorize (this|the)\b", r"\bintent classification\b"],
        0.90
    )
]

def check_code_presence(text: str) -> bool:
    if "```" in text:
        return True
    code_indicators = ["def ", "class ", "function ", "import ", "const ", "let ", "var ", "public static void ", "return "]
    matches = sum(1 for ind in code_indicators if ind in text)
    return matches >= 2
