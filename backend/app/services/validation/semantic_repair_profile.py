from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class SemanticRepairProfile:
    enable_sentence_repair: bool = True
    enable_code_repair: bool = True
    enable_table_repair: bool = True
    enable_formula_repair: bool = True
    enable_heading_repair: bool = True
    enable_overlap_repair: bool = True
    enable_metadata_repair: bool = True
    enable_retrieval_repair: bool = True
    enable_score_repair: bool = True
    enable_chunk_merge: bool = True
    enable_chunk_split: bool = True
    enable_duplicate_cleanup: bool = True
    strict_mode: bool = False
    repair_version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enable_sentence_repair": self.enable_sentence_repair,
            "enable_code_repair": self.enable_code_repair,
            "enable_table_repair": self.enable_table_repair,
            "enable_formula_repair": self.enable_formula_repair,
            "enable_heading_repair": self.enable_heading_repair,
            "enable_overlap_repair": self.enable_overlap_repair,
            "enable_metadata_repair": self.enable_metadata_repair,
            "enable_retrieval_repair": self.enable_retrieval_repair,
            "enable_score_repair": self.enable_score_repair,
            "enable_chunk_merge": self.enable_chunk_merge,
            "enable_chunk_split": self.enable_chunk_split,
            "enable_duplicate_cleanup": self.enable_duplicate_cleanup,
            "strict_mode": self.strict_mode,
            "repair_version": self.repair_version
        }
