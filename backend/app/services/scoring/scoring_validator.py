import math
from typing import List, Dict, Any, Union

class ValidationReport:
    def __init__(self):
        self.is_valid: bool = True
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def add_error(self, message: str):
        self.is_valid = False
        self.errors.append(message)

    def add_warning(self, message: str):
        self.warnings.append(message)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings
        }

    def summary(self) -> str:
        return f"Scoring validation status: {'VALID' if self.is_valid else 'INVALID'}. Errors: {len(self.errors)}, Warnings: {len(self.warnings)}."


class ScoringValidator:
    @staticmethod
    def validate(target: Union[Any, List[Any]]) -> ValidationReport:
        if isinstance(target, list):
            return ScoringValidator.validate_pipeline(target)
        
        report = ValidationReport()
        if not target:
            report.add_error("Null score object validation target.")
            return report

        # Single score validation
        ScoringValidator._validate_single(target, report, 0)
        return report

    @staticmethod
    def validate_pipeline(scores: List[Any]) -> ValidationReport:
        report = ValidationReport()
        if not scores:
            report.add_warning("No scores evaluated.")
            return report

        hashes = set()
        signatures = set()

        for idx, s in enumerate(scores):
            # Check duplicate hashes
            h = s.score_hash
            if h in hashes:
                report.add_error(f"Duplicate score hash detected: {h} at index {idx}")
            hashes.add(h)

            # Check duplicate signatures
            sig = s.score_signature
            if sig in signatures:
                report.add_error(f"Duplicate signature detected: {sig} at index {idx}")
            signatures.add(sig)

            ScoringValidator._validate_single(s, report, idx)

        return report

    @staticmethod
    def _validate_single(s: Any, report: ValidationReport, idx: int) -> None:
        # Check Ranges and NaNs/Infinities
        for name, score_val in [
            ("overall_score", s.overall_score),
            ("ranking_score", s.ranking_score),
            ("retrieval_priority", s.retrieval_priority),
            ("context_priority", s.context_priority),
            ("quality_score", s.quality_score)
        ]:
            if math.isnan(score_val):
                report.add_error(f"NaN value detected in field {name} at index {idx}")
            elif math.isinf(score_val):
                report.add_error(f"Infinity value detected in field {name} at index {idx}")
            elif not (0.0 <= score_val <= 1.0):
                report.add_error(f"Out of range [0,1] value in {name}: {score_val} at index {idx}")

        # Check missing properties
        if not s.explanation or not s.explanation.strip():
            report.add_error(f"Missing explanation at index {idx}")

        if not s.quality_breakdown:
            report.add_error(f"Missing quality breakdown at index {idx}")

        if s.recommendation not in {"HIGH_PRIORITY", "GOOD_FOR_RETRIEVAL", "MERGE_CANDIDATE", "SPLIT_CANDIDATE", "LOW_QUALITY", "CONTEXT_EXPANSION", "HYBRID_RETRIEVAL"}:
            report.add_warning(f"Non-standard recommendation category: {s.recommendation} at index {idx}")
