"""
Lightweight deterministic query rewriter for FTS queries.

Strategy
--------
1. Lowercase the input.
2. Strip punctuation (preserve Unicode letters, digits, whitespace).
3. Remove Vietnamese functional / grammatical stop words.
4. Collapse duplicate whitespace.
5. Safety net: if stop-word removal empties the result, return the
   punctuation-stripped + lowercased version without stop-word removal.

Design constraints
------------------
* Pure Python, zero external dependencies.
* No AI / LLM calls.
* Deterministic and fast (<1 ms for typical queries).
* Does NOT alter the original user message used for prompt construction.
"""
from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Punctuation & whitespace patterns
# ---------------------------------------------------------------------------
_PUNCT_RE = re.compile(r"[^\w\s]", re.UNICODE)
_SPACE_RE = re.compile(r"\s+")

# ---------------------------------------------------------------------------
# Vietnamese stop words — functional / grammatical words only.
# Technical and domain-specific words are intentionally excluded.
# ---------------------------------------------------------------------------
_STOP_WORDS: frozenset[str] = frozenset(
    {
        # Question particles
        "gì", "thế", "nào", "sao", "đâu", "ai", "ư", "hả", "nhỉ", "nhé",
        # Copula / light verbs
        "là", "được", "đã", "sẽ", "đang", "bị", "bởi",
        # Prepositions / spatial / temporal
        "trong", "ngoài", "của", "với", "cho", "từ", "về", "tại", "vào",
        "ra", "lên", "xuống", "theo", "trên", "dưới", "trước", "sau",
        "giữa", "qua", "tới", "đến", "lúc", "khi",
        # Conjunctions / connectors
        "và", "hoặc", "hay", "nhưng", "mà", "vì", "nếu", "như", "thì",
        "do", "để", "dù", "tuy",
        # Demonstratives / articles
        "các", "những", "một", "này", "đó", "ấy", "kia", "đây", "mọi",
        "toàn", "tất", "cả",
        # Intensifiers / fillers
        "rất", "quá", "khá", "cũng", "vẫn", "còn", "lại", "nữa", "thêm",
        "chỉ", "đều", "cùng", "nhau", "thật", "hơn", "kém", "nhất",
    }
)


def rewrite_query(query: str) -> str:
    """
    Return a normalized, stop-word-filtered version of *query* for FTS use.

    The original query string is never mutated and should still be used
    for prompt construction and display purposes.

    Parameters
    ----------
    query : str
        Raw user query as typed.

    Returns
    -------
    str
        Cleaned query suitable for PostgreSQL websearch_to_tsquery.
        Guaranteed to be non-empty as long as *query* itself is non-empty.

    Examples
    --------
    "Bien ngau nhien trong xac suat thong ke la gi"
    -> "bien ngau nhien xac suat thong ke"

    "What is a random variable?"
    -> "what is a random variable"

    "la gi"   # all stop words -> normalized fallback returned
    -> "la gi"
    """
    # 1. Lowercase
    text = query.lower().strip()

    # 2. Remove punctuation (keep Unicode letters / digits / whitespace)
    text = _PUNCT_RE.sub(" ", text)

    # 3. Collapse whitespace
    text = _SPACE_RE.sub(" ", text).strip()

    # 4. Remove stop words
    tokens = text.split()
    filtered = [tok for tok in tokens if tok not in _STOP_WORDS]
    rewritten = " ".join(filtered).strip()

    # 5. Safety net: stop-word removal emptied the query -> return normalized
    return rewritten if rewritten else text
