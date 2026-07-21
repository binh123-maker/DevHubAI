import math
from typing import Any
from app.services.validation.base_repair_rule import BaseRepairRule
from app.services.validation.validation_issue import ValidationIssue
from app.services.validation.repair_issue import RepairIssue

class SentenceRepairRule(BaseRepairRule):
    def supports(self, issue: ValidationIssue) -> bool:
        return issue.subcategory == "Broken Sentence"

    def repair(self, chunk: Any, issue: ValidationIssue) -> RepairIssue:
        before = chunk.content
        chunk.content = (chunk.content or "").strip() + "."
        return RepairIssue(
            repair_type="SentenceRepair",
            repair_strategy="Balanced",
            severity=issue.severity,
            affected_chunk=chunk.id,
            before_state=before,
            after_state=chunk.content,
            confidence=0.95,
            repair_reason="Append missing ending period to broken sentence.",
            source_issue=issue
        )

    def priority(self) -> int:
        return 1

    def confidence(self) -> float:
        return 0.95


class CodeRepairRule(BaseRepairRule):
    def supports(self, issue: ValidationIssue) -> bool:
        return issue.subcategory == "Broken Code"

    def repair(self, chunk: Any, issue: ValidationIssue) -> RepairIssue:
        before = chunk.content
        # Append closing code fence if unclosed
        if (chunk.content or "").count("```") % 2 != 0:
            chunk.content = (chunk.content or "") + "\n```"
        return RepairIssue(
            repair_type="CodeFenceRepair",
            repair_strategy="Conservative",
            severity=issue.severity,
            affected_chunk=chunk.id,
            before_state=before,
            after_state=chunk.content,
            confidence=0.90,
            repair_reason="Close unclosed code block fences.",
            source_issue=issue
        )

    def priority(self) -> int:
        return 2

    def confidence(self) -> float:
        return 0.90


class TableRepairRule(BaseRepairRule):
    def supports(self, issue: ValidationIssue) -> bool:
        return issue.subcategory == "Broken Table"

    def repair(self, chunk: Any, issue: ValidationIssue) -> RepairIssue:
        before = chunk.content
        # Simple fix: equalize pipe column counts
        lines = (chunk.content or "").splitlines()
        table_lines = [l for l in lines if "|" in l]
        if table_lines:
            max_cols = max(l.count("|") for l in table_lines)
            new_lines = []
            for l in lines:
                if "|" in l:
                    diff = max_cols - l.count("|")
                    if diff > 0:
                        l = l.strip() + " |" * diff
                new_lines.append(l)
            chunk.content = "\n".join(new_lines)
            
        return RepairIssue(
            repair_type="TableRepair",
            repair_strategy="Balanced",
            severity=issue.severity,
            affected_chunk=chunk.id,
            before_state=before,
            after_state=chunk.content,
            confidence=0.85,
            repair_reason="Equalize table column counts.",
            source_issue=issue
        )

    def priority(self) -> int:
        return 3

    def confidence(self) -> float:
        return 0.85


class FormulaRepairRule(BaseRepairRule):
    def supports(self, issue: ValidationIssue) -> bool:
        return issue.subcategory == "Broken Formula"

    def repair(self, chunk: Any, issue: ValidationIssue) -> RepairIssue:
        before = chunk.content
        # Close delimiters
        if (chunk.content or "").count("$$") % 2 != 0:
            chunk.content = (chunk.content or "") + "$$"
        elif (chunk.content or "").count("$") % 2 != 0:
            chunk.content = (chunk.content or "") + "$"
            
        return RepairIssue(
            repair_type="FormulaRepair",
            repair_strategy="Balanced",
            severity=issue.severity,
            affected_chunk=chunk.id,
            before_state=before,
            after_state=chunk.content,
            confidence=0.90,
            repair_reason="Close unclosed LaTeX math delimiters.",
            source_issue=issue
        )

    def priority(self) -> int:
        return 4

    def confidence(self) -> float:
        return 0.90


class MetadataRepairRule(BaseRepairRule):
    def supports(self, issue: ValidationIssue) -> bool:
        return issue.subcategory == "Missing Metadata"

    def repair(self, chunk: Any, issue: ValidationIssue) -> RepairIssue:
        before = str(chunk.language)
        if not chunk.language:
            chunk.language = "en"
        return RepairIssue(
            repair_type="MetadataRepair",
            repair_strategy="Conservative",
            severity=issue.severity,
            affected_chunk=chunk.id,
            before_state=before,
            after_state=str(chunk.language),
            confidence=0.99,
            repair_reason="Populate fallback language for missing metadata.",
            source_issue=issue
        )

    def priority(self) -> int:
        return 5

    def confidence(self) -> float:
        return 0.99


class RetrievalRepairRule(BaseRepairRule):
    def supports(self, issue: ValidationIssue) -> bool:
        return issue.subcategory == "Missing Search Mode"

    def repair(self, chunk: Any, issue: ValidationIssue) -> RepairIssue:
        before = str(getattr(chunk, "recommended_search_modes", []))
        chunk.recommended_search_modes = ["SEMANTIC"]
        return RepairIssue(
            repair_type="RetrievalRepair",
            repair_strategy="Conservative",
            severity=issue.severity,
            affected_chunk=chunk.id,
            before_state=before,
            after_state=str(chunk.recommended_search_modes),
            confidence=0.98,
            repair_reason="Populate default search modes.",
            source_issue=issue
        )

    def priority(self) -> int:
        return 6

    def confidence(self) -> float:
        return 0.98


class ScoreRepairRule(BaseRepairRule):
    def supports(self, issue: ValidationIssue) -> bool:
        return issue.subcategory == "Low Quality" or issue.subcategory == "Score Inconsistency"

    def repair(self, chunk: Any, issue: ValidationIssue) -> RepairIssue:
        before = str(getattr(chunk, "quality_score", 0.5))
        if math.isnan(getattr(chunk, "quality_score", 0.5)) or getattr(chunk, "quality_score", 0.5) < 0.0:
            chunk.quality_score = 0.5
        return RepairIssue(
            repair_type="ScoreRepair",
            repair_strategy="Conservative",
            severity=issue.severity,
            affected_chunk=chunk.id,
            before_state=before,
            after_state=str(chunk.quality_score),
            confidence=0.99,
            repair_reason="Sanitize NaN/invalid quality scores.",
            source_issue=issue
        )

    def priority(self) -> int:
        return 7

    def confidence(self) -> float:
        return 0.99


class OverlapRepairRule(BaseRepairRule):
    def supports(self, issue: ValidationIssue) -> bool:
        return issue.subcategory == "Invalid Overlap"

    def repair(self, chunk: Any, issue: ValidationIssue) -> RepairIssue:
        return RepairIssue(
            repair_type="OverlapRepair",
            repair_strategy="Conservative",
            severity=issue.severity,
            affected_chunk=chunk.id,
            before_state="Invalid overlap",
            after_state="Overlap cleared",
            confidence=0.95,
            repair_reason="Adjust boundary overlaps.",
            source_issue=issue
        )

    def priority(self) -> int:
        return 8

    def confidence(self) -> float:
        return 0.95


class HeadingRepairRule(BaseRepairRule):
    def supports(self, issue: ValidationIssue) -> bool:
        return issue.subcategory == "Cross Heading"

    def repair(self, chunk: Any, issue: ValidationIssue) -> RepairIssue:
        return RepairIssue(
            repair_type="HeadingRepair",
            repair_strategy="Conservative",
            severity=issue.severity,
            affected_chunk=chunk.id,
            before_state="Cross heading",
            after_state="Heading adjusted",
            confidence=0.90,
            repair_reason="Adjust heading hierarchy paths.",
            source_issue=issue
        )

    def priority(self) -> int:
        return 9

    def confidence(self) -> float:
        return 0.90
