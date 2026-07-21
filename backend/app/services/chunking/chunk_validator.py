from typing import List, Dict, Any

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
        return f"Chunk validation status: {status}. Errors: {len(self.errors)}, Warnings: {len(self.warnings)}."

    def pretty_print(self) -> str:
        errs = "\n".join([f"  - ERROR: {e}" for e in self.errors])
        warns = "\n".join([f"  - WARNING: {w}" for w in self.warnings])
        return (
            f"=== Chunk Validation Report ===\n"
            f"Status: {'VALID' if self.is_valid else 'INVALID'}\n"
            f"Errors ({len(self.errors)}):\n{errs if errs else '  None'}\n"
            f"Warnings ({len(self.warnings)}):\n{warns if warns else '  None'}"
        )


class ChunkValidator:
    @staticmethod
    def validate(chunks: List[Any], original_units: List[Any] = None) -> ValidationReport:
        report = ValidationReport()
        if not chunks:
            report.add_warning("No chunks generated for validation.")
            return report

        chunk_ids = set()
        hashes = set()
        fingerprints = set()
        signatures = set()
        all_referenced_unit_ids = set()

        for idx, chunk in enumerate(chunks):
            cid = str(chunk.id)
            if cid in chunk_ids:
                report.add_error(f"Duplicate chunk ID detected: {cid}")
            chunk_ids.add(cid)

            chash = chunk.chunk_hash
            if chash in hashes:
                report.add_error(f"Duplicate chunk hash detected: {chash}")
            hashes.add(chash)

            fp = chunk.fingerprint
            if fp in fingerprints:
                report.add_error(f"Duplicate fingerprint detected: {fp}")
            fingerprints.add(fp)

            # 10.3D extended validations
            sig = chunk.chunk_signature
            if sig in signatures:
                report.add_error(f"Duplicate signature detected: {sig}")
            signatures.add(sig)

            # Validate empty content
            if not chunk.content or not chunk.content.strip():
                report.add_error(f"Chunk at index {chunk.chunk_index} is empty.")

            # Validate token count
            if chunk.estimated_tokens <= 0:
                report.add_error(f"Chunk {cid} has invalid token count: {chunk.estimated_tokens}")

            # Validate quality thresholds
            if not (0.0 <= chunk.quality_score <= 1.0):
                report.add_error(f"Chunk {cid} has invalid quality_score: {chunk.quality_score}")
            if not (0.0 <= chunk.importance_score <= 1.0):
                report.add_error(f"Chunk {cid} has invalid importance_score: {chunk.importance_score}")

            # Validate overlaps
            if chunk.overlap_before and chunk.overlap_before == chunk.content[:len(chunk.overlap_before)]:
                report.add_warning(f"Chunk {cid} has duplicate prefix overlap.")

            for u in chunk.semantic_units:
                all_referenced_unit_ids.add(u.id)

        # Orphan units
        if original_units:
            orig_unit_ids = {u.id for u in original_units}
            orphans = orig_unit_ids - all_referenced_unit_ids
            if orphans:
                report.add_error(f"Orphan semantic units detected (not assigned to any chunk): {orphans}")

        return report
