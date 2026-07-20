import uuid
from typing import List, Dict, Any, Optional

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
        status = "VALID" if self.is_valid else "INVALID"
        return f"Boundary map status: {status}. Errors: {len(self.errors)}, Warnings: {len(self.warnings)}."


class SemanticBoundaryValidator:
    @staticmethod
    def validate(units: List[Any], boundaries: List[Any]) -> ValidationReport:
        report = ValidationReport()
        if not units:
            if boundaries:
                report.add_error("Boundaries exist but no semantic units exist.")
            return report

        unit_ids = {u.id for u in units}
        
        # 1. No Duplicate Boundaries & Invalid References & Confidence Range
        seen_transitions = set()
        prev_offset = -1
        
        for idx, b in enumerate(boundaries):
            # Check duplicate transitions
            transition = (b.previous_unit_id, b.next_unit_id)
            if transition in seen_transitions:
                report.add_error(f"Duplicate boundary transition detected: {transition}")
            seen_transitions.add(transition)

            # Check invalid references
            if b.previous_unit_id and b.previous_unit_id not in unit_ids:
                report.add_error(f"Boundary {b.id} references non-existent previous unit {b.previous_unit_id}")
            if b.next_unit_id and b.next_unit_id not in unit_ids:
                report.add_error(f"Boundary {b.id} references non-existent next unit {b.next_unit_id}")

            # Check confidence range
            if not (0.0 <= b.final_confidence <= 1.0):
                report.add_error(f"Boundary {b.id} has final confidence {b.final_confidence} out of range [0.0, 1.0]")

            # Check ordering correct (non-decreasing character offset)
            if b.char_offset is not None:
                if b.char_offset < prev_offset:
                    report.add_error(f"Boundary {b.id} has out-of-order char_offset: {b.char_offset} < {prev_offset}")
                prev_offset = b.char_offset

        # 2. Every Unit Connected (No orphan units)
        connected_units = set()
        for b in boundaries:
            if b.previous_unit_id:
                connected_units.add(b.previous_unit_id)
            if b.next_unit_id:
                connected_units.add(b.next_unit_id)
                
        orphan_units = unit_ids - connected_units
        if orphan_units:
            report.add_error(f"Orphan semantic units detected (not connected to any boundary): {orphan_units}")

        # 3. Graph Consistency
        # The first boundary must have previous_unit_id = None or we must be able to trace from first to last
        if boundaries and len(units) > 1:
            # Let's count boundary count
            expected_boundaries = len(units) # N-1 transitions + 1 doc end
            if len(boundaries) != expected_boundaries:
                report.add_warning(f"Boundary count mismatch. Expected {expected_boundaries}, got {len(boundaries)}.")

        return report
