"""
Pipeline Explanation Report — Phase 10.6

Generates Markdown, JSON, HTML, and Pretty-Print reports from a pipeline context.
"""
from __future__ import annotations
import json
from typing import Any, Dict, List, Optional


class PipelineExplanationReport:
    """Generates human-readable and machine-readable pipeline reports."""

    def __init__(self, ctx: Any, metrics: Any = None, statistics: Any = None, health: Any = None) -> None:
        self._ctx = ctx
        self._metrics = metrics
        self._statistics = statistics
        self._health = health

    # ------------------------------------------------------------------ Markdown
    def to_markdown(self) -> str:
        ctx = self._ctx
        lines = [
            "# Pipeline Execution Report",
            "",
            f"**Pipeline ID**: `{getattr(ctx, 'pipeline_id', 'N/A')}`  ",
            f"**Status**: {getattr(ctx, 'pipeline_status', 'N/A')}  ",
            f"**Health**: {getattr(ctx, 'pipeline_health', 0.0):.2f}  ",
            f"**Fallback Used**: {getattr(ctx, 'fallback_used', False)}  ",
            f"**Total Elapsed**: {getattr(ctx, 'total_elapsed', lambda: 0.0)():.3f}s  ",
            "",
            "## Execution Summary",
            "",
            f"- Chunks: **{len(getattr(ctx, 'chunks', []))}**",
            f"- Scores: **{len(getattr(ctx, 'scores', []))}**",
            f"- Events: **{len(getattr(ctx, 'events', []))}**",
            "",
            "## Stage Timings",
            "",
        ]
        for stage, elapsed in (getattr(ctx, "stage_timings", {}) or {}).items():
            lines.append(f"- `{stage}`: {elapsed:.3f}s")

        if self._health:
            lines += ["", "## Health Summary", ""]
            h = self._health
            lines += [
                f"- Level: **{getattr(h, 'level', 'N/A')}**",
                f"- Score: {getattr(h, 'health_score', 0.0):.3f}",
                f"- Success Rate: {getattr(h, 'success_rate', 0.0):.1%}",
                f"- Fallback Rate: {getattr(h, 'fallback_rate', 0.0):.1%}",
            ]

        if self._metrics:
            m = self._metrics
            lines += ["", "## Metrics", ""]
            lines += [
                f"- Documents Processed: {getattr(m, 'documents_processed', 0)}",
                f"- Successful: {getattr(m, 'successful_pipelines', 0)}",
                f"- Failed: {getattr(m, 'failed_pipelines', 0)}",
                f"- Avg Execution Time: {getattr(m, 'average_execution_time', 0.0):.3f}s",
                f"- Retry Count: {getattr(m, 'retry_count', 0)}",
                f"- Cache Hits: {getattr(m, 'cache_hits', 0)}",
            ]

        if self._statistics:
            s = self._statistics
            lines += ["", "## Statistics", ""]
            lines += [
                f"- Total Chunks: {getattr(s, 'total_chunks', 0)}",
                f"- Avg Chunks/Doc: {getattr(s, 'average_chunks', 0.0):.1f}",
                f"- Avg Score: {getattr(s, 'average_score', 0.0):.3f}",
                f"- Validation Passed: {getattr(s, 'validation_passed', 0)}",
                f"- Repair Count: {getattr(s, 'repair_count', 0)}",
                f"- Pipeline Success Rate: {getattr(s, 'pipeline_success_rate', 1.0):.1%}",
            ]

        return "\n".join(lines)

    # ------------------------------------------------------------------ JSON
    def to_json(self, indent: int = 2) -> str:
        ctx = self._ctx
        data: Dict[str, Any] = {
            "pipeline_id": getattr(ctx, "pipeline_id", ""),
            "pipeline_status": getattr(ctx, "pipeline_status", ""),
            "pipeline_health": getattr(ctx, "pipeline_health", 0.0),
            "fallback_used": getattr(ctx, "fallback_used", False),
            "stage_timings": getattr(ctx, "stage_timings", {}),
            "chunk_count": len(getattr(ctx, "chunks", [])),
            "score_count": len(getattr(ctx, "scores", [])),
        }
        if self._health:
            data["health"] = getattr(self._health, "to_dict", lambda: {})()
        if self._metrics:
            data["metrics"] = getattr(self._metrics, "to_dict", lambda: {})()
        if self._statistics:
            data["statistics"] = getattr(self._statistics, "to_dict", lambda: {})()
        return json.dumps(data, indent=indent)

    # ------------------------------------------------------------------ Pretty Print
    def pretty_print(self) -> str:
        ctx = self._ctx
        sep = "=" * 60
        lines = [
            sep,
            " PIPELINE EXECUTION REPORT",
            sep,
            f" ID      : {getattr(ctx, 'pipeline_id', 'N/A')}",
            f" Status  : {getattr(ctx, 'pipeline_status', 'N/A')}",
            f" Health  : {getattr(ctx, 'pipeline_health', 0.0):.2f}",
            f" Chunks  : {len(getattr(ctx, 'chunks', []))}",
            f" Fallback: {getattr(ctx, 'fallback_used', False)}",
            sep,
            " Stage Timings:",
        ]
        for stage, elapsed in (getattr(ctx, "stage_timings", {}) or {}).items():
            lines.append(f"   {stage:<35} {elapsed:.3f}s")
        lines.append(sep)
        return "\n".join(lines)

    # ------------------------------------------------------------------ HTML
    def to_html(self) -> str:
        ctx = self._ctx
        stage_rows = "".join(
            f"<tr><td><code>{s}</code></td><td>{e:.3f}s</td></tr>"
            for s, e in (getattr(ctx, "stage_timings", {}) or {}).items()
        )
        return f"""<!DOCTYPE html>
<html><head><title>Pipeline Report</title></head>
<body>
<h1>Pipeline Execution Report</h1>
<p><strong>ID</strong>: <code>{getattr(ctx, 'pipeline_id', '')}</code></p>
<p><strong>Status</strong>: {getattr(ctx, 'pipeline_status', '')}</p>
<p><strong>Health</strong>: {getattr(ctx, 'pipeline_health', 0.0):.2f}</p>
<p><strong>Chunks</strong>: {len(getattr(ctx, 'chunks', []))}</p>
<h2>Stage Timings</h2>
<table border="1"><thead><tr><th>Stage</th><th>Elapsed</th></tr></thead>
<tbody>{stage_rows}</tbody></table>
</body></html>"""
