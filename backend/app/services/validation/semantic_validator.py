import time
from typing import List, Optional, Any, Dict
from app.services.validation.semantic_validation_profile import SemanticValidationProfile
from app.services.validation.semantic_validation_result import SemanticValidationResult
from app.services.validation.validation_issue import ValidationIssue
from app.services.validation.validation_rules import (
    validate_sentence,
    validate_code,
    validate_table,
    validate_formula,
    validate_quality,
    validate_boundary,
    validate_retrieval
)
from app.services.validation.validation_cache import ValidationCache

class SemanticValidator:
    @staticmethod
    def validate_chunk(chunk: Any, profile: Optional[SemanticValidationProfile] = None) -> SemanticValidationResult:
        start_time = time.time()
        profile = profile or SemanticValidationProfile()
        cache = ValidationCache()
        
        # Cache lookup
        fp = getattr(chunk, "fingerprint", "")
        cached = cache.get(fp, profile.validation_version)
        if cached:
            return cached

        issues: List[ValidationIssue] = []
        
        # Execute Rules
        issues.extend(validate_sentence(chunk))
        issues.extend(validate_code(chunk))
        issues.extend(validate_table(chunk))
        issues.extend(validate_formula(chunk))
        issues.extend(validate_quality(chunk, profile))
        issues.extend(validate_boundary(chunk, profile))
        issues.extend(validate_retrieval(chunk))

        # Scoring metrics
        critical_count = sum(1 for i in issues if i.severity == "CRITICAL")
        warning_count = sum(1 for i in issues if i.severity == "WARNING")
        
        overall_score = 1.0 - (critical_count * 0.40 + warning_count * 0.15)
        overall_score = round(max(0.0, min(1.0, overall_score)), 2)

        result = SemanticValidationResult(
            validation_version=profile.validation_version,
            overall_validation_score=overall_score,
            pipeline_health_score=overall_score,
            retrieval_readiness_score=overall_score,
            semantic_quality_score=overall_score,
            total_rules=7,
            passed_rules=7 - len(issues),
            failed_rules=len(issues),
            issues=issues,
            recommendations=[i.recommendation for i in issues],
            execution_time=time.time() - start_time
        )
        
        # Cache result
        cache.set(fp, profile.validation_version, result)
        return result

    @staticmethod
    def validate_chunks(chunks: List[Any], profile: Optional[SemanticValidationProfile] = None) -> List[SemanticValidationResult]:
        profile = profile or SemanticValidationProfile()
        return [SemanticValidator.validate_chunk(c, profile) for c in chunks]

    @staticmethod
    def validate_pipeline(chunks: List[Any], profile: Optional[SemanticValidationProfile] = None) -> SemanticValidationResult:
        profile = profile or SemanticValidationProfile()
        results = SemanticValidator.validate_chunks(chunks, profile)
        
        all_issues = []
        for r in results:
            all_issues.extend(r.issues)
            
        critical = sum(1 for i in all_issues if i.severity == "CRITICAL")
        warning = sum(1 for i in all_issues if i.severity == "WARNING")
        
        avg_score = sum(r.overall_validation_score for r in results) / len(results) if results else 1.0
        
        return SemanticValidationResult(
            validation_version=profile.validation_version,
            overall_validation_score=avg_score,
            pipeline_health_score=avg_score,
            retrieval_readiness_score=avg_score,
            semantic_quality_score=avg_score,
            total_rules=7 * len(chunks),
            passed_rules=7 * len(chunks) - len(all_issues),
            failed_rules=len(all_issues),
            issues=all_issues,
            recommendations=[i.recommendation for i in all_issues]
        )

    # Sub-component validation stubs
    @staticmethod
    def validate_scores(scores: List[Any]) -> bool:
        return True

    @staticmethod
    def validate_metadata(chunks: List[Any]) -> bool:
        return True

    @staticmethod
    def validate_lineage(chunks: List[Any]) -> bool:
        return True

    @staticmethod
    def validate_retrieval(chunks: List[Any]) -> bool:
        return True

    @staticmethod
    def validate_explainability(chunks: List[Any]) -> bool:
        return True

    @staticmethod
    def validate_graph(graph: Any) -> bool:
        return True
