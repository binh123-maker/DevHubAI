import re
from typing import List, Dict, Any, Tuple

class ChunkIntelligenceAnalyzer:
    @staticmethod
    def calculate_heading_relevance(heading_path: List[str], content: str) -> float:
        if not heading_path:
            return 0.5
        words = []
        for h in heading_path:
            words.extend(re.findall(r'\b\w{3,}\b', h.lower()))
        if not words:
            return 0.5
            
        content_lower = content.lower()
        matched = sum(1 for w in set(words) if w in content_lower)
        return round(matched / len(set(words)), 2)

    @staticmethod
    def calculate_code_density(units: List[Any]) -> float:
        if not units:
            return 0.0
        code_chars = sum(len(u.content) for u in units if getattr(u, "semantic_type", "") == "code")
        total_chars = sum(len(u.content) for u in units)
        return round(code_chars / total_chars, 2) if total_chars > 0 else 0.0

    @staticmethod
    def calculate_formula_density(units: List[Any]) -> float:
        if not units:
            return 0.0
        formula_chars = sum(len(u.content) for u in units if getattr(u, "semantic_type", "") == "formula")
        total_chars = sum(len(u.content) for u in units)
        return round(formula_chars / total_chars, 2) if total_chars > 0 else 0.0

    @staticmethod
    def calculate_table_density(units: List[Any]) -> float:
        if not units:
            return 0.0
        table_chars = sum(len(u.content) for u in units if getattr(u, "semantic_type", "") == "table")
        total_chars = sum(len(u.content) for u in units)
        return round(table_chars / total_chars, 2) if total_chars > 0 else 0.0

    @staticmethod
    def calculate_readability(content: str) -> float:
        if not content:
            return 0.0
        words = content.split()
        if not words:
            return 0.0
        avg_word_len = sum(len(w) for w in words) / len(words)
        # Normalize: average english word length is ~5.1. Longer words => lower readability.
        score = 1.0 - (avg_word_len - 4.0) / 6.0
        return round(min(1.0, max(0.1, score)), 2)

    @staticmethod
    def calculate_boundary_confidence(boundaries: List[Any]) -> float:
        if not boundaries:
            return 0.8
        conf = sum(getattr(b, "final_confidence", 0.5) for b in boundaries) / len(boundaries)
        return round(conf, 2)

    @staticmethod
    def detect_chunk_type(units: List[Any]) -> str:
        if not units:
            return "TEXT"
        counts = {}
        for u in units:
            t = getattr(u, "semantic_type", "paragraph").upper()
            counts[t] = counts.get(t, 0) + len(u.content)
        if not counts:
            return "TEXT"
        # Find dominant type by character count
        dominant = max(counts, key=counts.get)
        return dominant

    @staticmethod
    def generate_retrieval_hints(units: List[Any]) -> Dict[str, Any]:
        types = {getattr(u, "semantic_type", "").lower() for u in units}
        return {
            "contains_code": "code" in types,
            "contains_table": "table" in types,
            "contains_formula": "formula" in types,
            "contains_warning": "warning" in types,
            "contains_definition": "definition" in types,
            "contains_example": "example" in types,
            "contains_question": "question" in types,
            "contains_answer": "answer" in types
        }

    @staticmethod
    def detect_search_modes(hints: Dict[str, bool]) -> List[str]:
        modes = ["SEMANTIC"]
        if hints.get("contains_code"):
            modes.append("CODE")
        if hints.get("contains_table") or hints.get("contains_formula"):
            modes.append("HYBRID")
        else:
            modes.append("FULLTEXT")
        return modes

    @staticmethod
    def calculate_retrieval_weight(importance_score: float, code_density: float, table_density: float) -> float:
        # Boost retrieval weight based on technical densities
        base = importance_score * 1.2
        boost = code_density * 0.15 + table_density * 0.10
        return round(min(2.0, max(0.5, base + boost)), 2)

    @staticmethod
    def calculate_chunk_quality(breakdown: Dict[str, float]) -> float:
        if not breakdown:
            return 0.8
        return round(sum(breakdown.values()) / len(breakdown), 2)
