"""
Pipeline Manifest — Phase 10.6

Generates a deterministic, versioned description of the pipeline.
Supports JSON and Markdown export.
"""
from __future__ import annotations
import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class StageManifestEntry:
    name: str
    version: str
    dependencies: List[str]
    enabled: bool


@dataclass
class PipelineManifest:
    """Deterministic snapshot of the pipeline configuration."""

    pipeline_version: str = "1.0.0"
    manifest_version: str = "1.0"
    generated_at: float = field(default_factory=time.time)

    stages: List[StageManifestEntry] = field(default_factory=list)
    execution_order: List[str] = field(default_factory=list)

    scoring_version: str = ""
    validation_version: str = ""
    repair_version: str = ""

    profile_name: str = "production"
    configuration: Dict[str, Any] = field(default_factory=dict)

    pipeline_fingerprint: str = ""
    execution_hash: str = ""

    # ------------------------------------------------------------------
    def compute_fingerprint(self) -> str:
        payload = json.dumps({
            "pipeline_version": self.pipeline_version,
            "execution_order": self.execution_order,
            "scoring_version": self.scoring_version,
            "validation_version": self.validation_version,
            "repair_version": self.repair_version,
        }, sort_keys=True)
        self.pipeline_fingerprint = hashlib.sha256(payload.encode()).hexdigest()[:16]
        return self.pipeline_fingerprint

    def compute_execution_hash(self) -> str:
        payload = json.dumps({
            "fingerprint": self.pipeline_fingerprint,
            "generated_at": round(self.generated_at, 0),
            "stage_count": len(self.stages),
        }, sort_keys=True)
        self.execution_hash = hashlib.md5(payload.encode()).hexdigest()[:12]
        return self.execution_hash

    # ------------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pipeline_version": self.pipeline_version,
            "manifest_version": self.manifest_version,
            "profile_name": self.profile_name,
            "stages": [
                {
                    "name": s.name,
                    "version": s.version,
                    "dependencies": s.dependencies,
                    "enabled": s.enabled,
                }
                for s in self.stages
            ],
            "execution_order": self.execution_order,
            "scoring_version": self.scoring_version,
            "validation_version": self.validation_version,
            "repair_version": self.repair_version,
            "pipeline_fingerprint": self.pipeline_fingerprint,
            "execution_hash": self.execution_hash,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def to_markdown(self) -> str:
        lines = [
            f"# Pipeline Manifest",
            f"",
            f"**Version**: {self.pipeline_version}  ",
            f"**Profile**: {self.profile_name}  ",
            f"**Fingerprint**: `{self.pipeline_fingerprint}`  ",
            f"**Execution Hash**: `{self.execution_hash}`  ",
            f"",
            f"## Execution Order",
            f"",
        ]
        for i, name in enumerate(self.execution_order, 1):
            lines.append(f"{i}. `{name}`")
        lines += ["", "## Stages", ""]
        for s in self.stages:
            status = "✓" if s.enabled else "✗"
            deps = ", ".join(s.dependencies) or "none"
            lines.append(f"- {status} **{s.name}** v{s.version} ← deps: {deps}")
        lines += [
            "",
            "## Component Versions",
            "",
            f"- Scoring: `{self.scoring_version}`",
            f"- Validation: `{self.validation_version}`",
            f"- Repair: `{self.repair_version}`",
        ]
        return "\n".join(lines)
