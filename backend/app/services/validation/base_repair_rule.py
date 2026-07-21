import abc
from typing import Any
from app.services.validation.validation_issue import ValidationIssue
from app.services.validation.repair_issue import RepairIssue

class BaseRepairRule(abc.ABC):
    @abc.abstractmethod
    def supports(self, issue: ValidationIssue) -> bool:
        pass

    @abc.abstractmethod
    def repair(self, chunk: Any, issue: ValidationIssue) -> RepairIssue:
        pass

    @abc.abstractmethod
    def priority(self) -> int:
        pass

    @abc.abstractmethod
    def confidence(self) -> float:
        pass
