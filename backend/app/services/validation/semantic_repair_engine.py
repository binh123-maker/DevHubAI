import time
from typing import List, Dict, Any, Optional
from app.services.validation.semantic_validation_profile import SemanticValidationProfile
from app.services.validation.semantic_validation_result import SemanticValidationResult
from app.services.validation.semantic_repair_result import SemanticRepairResult
from app.services.validation.repair_issue import RepairIssue
from app.services.validation.repair_strategy import BaseRepairStrategy, BalancedRepairStrategy
from app.services.validation.repair_validator import RepairValidator
from app.services.validation.repair_rules import (
    SentenceRepairRule,
    CodeRepairRule,
    TableRepairRule,
    FormulaRepairRule,
    MetadataRepairRule,
    RetrievalRepairRule,
    ScoreRepairRule,
    OverlapRepairRule,
    HeadingRepairRule
)
from app.services.validation.semantic_validator import SemanticValidator

class SemanticRepairEngine:
    def __init__(
        self,
        strategy: Optional[BaseRepairStrategy] = None,
        validator: Optional[RepairValidator] = None,
        rules: Optional[List[Any]] = None
    ):
        self.strategy = strategy or BalancedRepairStrategy()
        self.validator = validator or RepairValidator()
        self.rules = rules or [
            SentenceRepairRule(),
            CodeRepairRule(),
            TableRepairRule(),
            FormulaRepairRule(),
            MetadataRepairRule(),
            RetrievalRepairRule(),
            ScoreRepairRule(),
            OverlapRepairRule(),
            HeadingRepairRule()
        ]

    def repair_chunks(
        self,
        chunks: List[Any],
        validation_result: SemanticValidationResult
    ) -> SemanticRepairResult:
        start_time = time.time()
        
        repaired_issues = []
        failed_repairs = []
        skipped_repairs = []
        
        chunk_map = {c.id: c for c in chunks}
        
        # Group issues by affected chunk
        for issue in validation_result.issues:
            target_chunk = chunk_map.get(issue.affected_chunk)
            if not target_chunk:
                skipped_repairs.append(issue)
                continue
                
            # Find rule
            applied = False
            for rule in sorted(self.rules, key=lambda r: r.priority()):
                if rule.supports(issue):
                    try:
                        repair_action = rule.repair(target_chunk, issue)
                        repaired_issues.append(repair_action)
                        applied = True
                        break
                    except Exception as e:
                        failed_repairs.append((issue, str(e)))
                        applied = True
                        break
            if not applied:
                skipped_repairs.append(issue)

        # Pre-validate repaired chunks
        self.validator.validate(chunks)

        # Trigger re-validation
        profile = SemanticValidationProfile()
        revalidated_res = SemanticValidator.validate_pipeline(chunks, profile)
        
        return SemanticRepairResult(
            repaired_chunks=chunks,
            repaired_issues=repaired_issues,
            skipped_repairs=skipped_repairs,
            failed_repairs=failed_repairs,
            repair_score=revalidated_res.overall_validation_score,
            repair_quality=revalidated_res.overall_validation_score,
            execution_time=time.time() - start_time
        )

    # Context & Strategy Helpers
    def repair_pipeline(self, chunks: List[Any], validation_result: SemanticValidationResult) -> SemanticRepairResult:
        return self.repair_chunks(chunks, validation_result)

    def repair_chunk(self, chunk: Any, issue: Any) -> Optional[RepairIssue]:
        for rule in self.rules:
            if rule.supports(issue):
                return rule.repair(chunk, issue)
        return None

    def repair_validation_result(self, validation_result: Any) -> Any:
        return validation_result

    def repair_metadata(self, chunks: List[Any]) -> List[Any]:
        return chunks

    def repair_scores(self, chunks: List[Any]) -> List[Any]:
        return chunks

    def repair_overlaps(self, chunks: List[Any]) -> List[Any]:
        return chunks

    def repair_retrieval(self, chunks: List[Any]) -> List[Any]:
        return chunks

    def repair_lineage(self, chunks: List[Any]) -> List[Any]:
        return chunks
