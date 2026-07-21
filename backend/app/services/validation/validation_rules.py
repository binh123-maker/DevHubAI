import re
from typing import List, Dict, Any, Optional
from app.services.validation.validation_issue import ValidationIssue

# --- Structural Rules ---

def validate_sentence(chunk: Any) -> List[ValidationIssue]:
    issues = []
    content = chunk.content or ""
    # Incomplete sentence: ends with normal word instead of punctuation
    if content and not content.strip().endswith(('.', '!', '?', '"', "'", '`')):
        issues.append(ValidationIssue(
            severity="WARNING",
            category="Structural",
            subcategory="Broken Sentence",
            rule_name="SentenceTerminationRule",
            affected_chunk=chunk.id,
            description="Chunk content ends without standard punctuation, indicating a broken sentence.",
            recommendation="Merge with subsequent chunk or append punctuation.",
            repair_hint="Append period to chunk content.",
            affected_units=[u.id for u in chunk.semantic_units] if hasattr(chunk, "semantic_units") else []
        ))
    return issues


def validate_code(chunk: Any) -> List[ValidationIssue]:
    issues = []
    content = chunk.content or ""
    # Check unclosed code fences
    fences = content.count("```")
    if fences % 2 != 0:
        issues.append(ValidationIssue(
            severity="CRITICAL",
            category="Structural",
            subcategory="Broken Code",
            rule_name="UnclosedCodeFenceRule",
            affected_chunk=chunk.id,
            description="Odd number of code block fences (```) detected, indicating an unclosed code fence.",
            recommendation="Append a closing code fence (```) at the end of the chunk.",
            repair_hint="Append ``` to chunk content."
        ))

    # Bracket mismatch
    for open_char, close_char, name in [('{', '}', 'Braces'), ('(', ')', 'Parentheses'), ('[', ']', 'Brackets')]:
        if content.count(open_char) != content.count(close_char):
            issues.append(ValidationIssue(
                severity="WARNING",
                category="Structural",
                subcategory="Broken Code",
                rule_name=f"Mismatched{name}Rule",
                affected_chunk=chunk.id,
                description=f"Mismatched count of {name}: {content.count(open_char)} opening vs {content.count(close_char)} closing.",
                recommendation=f"Balance the {name} formatting.",
                repair_hint="Review matching brackets."
            ))
            
    return issues


def validate_table(chunk: Any) -> List[ValidationIssue]:
    issues = []
    content = chunk.content or ""
    
    # Simple table validator: if it contains '|' it might be a table
    lines = content.splitlines()
    table_lines = [l for l in lines if "|" in l]
    
    if table_lines:
        # Check column mismatches
        col_counts = [l.count("|") for l in table_lines]
        if len(set(col_counts)) > 1:
            issues.append(ValidationIssue(
                severity="ERROR",
                category="Structural",
                subcategory="Broken Table",
                rule_name="TableColumnMismatchRule",
                affected_chunk=chunk.id,
                description="Markdown table column divider count mismatch across rows.",
                recommendation="Ensure all table rows contain consistent column divider counts.",
                repair_hint="Align column counts in table lines."
            ))
    return issues


def validate_formula(chunk: Any) -> List[ValidationIssue]:
    issues = []
    content = chunk.content or ""
    
    # Check mismatched LaTeX delimiters
    delimiters = ["$$", "$"]
    for delim in delimiters:
        # count occurrences. If count is odd, it's mismatched.
        # Note: replace $$ first to avoid overlapping count in inline $
        temp = content.replace("$$", "DOUBLE_DELIM")
        count = temp.count(delim) if delim == "$" else content.count("$$")
        if count % 2 != 0:
            issues.append(ValidationIssue(
                severity="ERROR",
                category="Structural",
                subcategory="Broken Formula",
                rule_name="LatexDelimiterMismatchRule",
                affected_chunk=chunk.id,
                description=f"Odd count of math delimiters ({delim}) indicating unclosed math mode.",
                recommendation=f"Close mismatched delimiter {delim}.",
                repair_hint=f"Append {delim} to chunk content."
            ))
    return issues


# --- Semantic Rules ---

def validate_quality(chunk: Any, profile: Any) -> List[ValidationIssue]:
    issues = []
    
    quality = getattr(chunk, "quality_score", 0.5)
    if quality < profile.minimum_quality_score:
        issues.append(ValidationIssue(
            severity="WARNING",
            category="Quality",
            subcategory="Low Quality",
            rule_name="LowQualityThresholdRule",
            affected_chunk=chunk.id,
            description=f"Quality score {quality:.2f} is below profile threshold {profile.minimum_quality_score:.2f}.",
            recommendation="Re-chunk or score chunk again.",
            repair_hint="Examine readability and headings."
        ))

    # Cohesion
    cohesion = chunk.quality_breakdown.get("semantic_cohesion", 0.8) if hasattr(chunk, "quality_breakdown") else 0.8
    if cohesion < profile.minimum_cohesion:
        issues.append(ValidationIssue(
            severity="WARNING",
            category="Semantic",
            subcategory="Low Cohesion",
            rule_name="LowCohesionThresholdRule",
            affected_chunk=chunk.id,
            description=f"Semantic cohesion {cohesion:.2f} is below cohesion threshold {profile.minimum_cohesion:.2f}.",
            recommendation="Merge chunk with adjacent ones.",
            repair_hint="Evaluate heading transitions."
        ))
    return issues


# --- Boundary Rules ---

def validate_boundary(chunk: Any, profile: Any) -> List[ValidationIssue]:
    issues = []
    
    # Heading crossing check
    headings = getattr(chunk, "heading_path", [])
    if len(headings) > 1 and not profile.allow_cross_heading:
        # Cross heading candidate
        pass
    
    return issues


# --- Retrieval Rules ---

def validate_retrieval(chunk: Any) -> List[ValidationIssue]:
    issues = []
    
    # Check recommended search modes
    modes = getattr(chunk, "recommended_search_modes", [])
    if not modes:
        issues.append(ValidationIssue(
            severity="WARNING",
            category="Retrieval",
            subcategory="Missing Search Mode",
            rule_name="MissingSearchModeRule",
            affected_chunk=chunk.id,
            description="Recommended search mode list is empty.",
            recommendation="Populate default search mode values.",
            repair_hint="Default to SEMANTIC."
        ))
    return issues
