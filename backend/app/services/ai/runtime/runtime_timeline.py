import time
import json
from typing import Dict, Any, List

class TimelineStep:
    def __init__(self, step_name: str, details: Dict[str, Any]):
        self.step_name = step_name
        self.timestamp = time.time()
        self.details = details

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step_name,
            "timestamp": self.timestamp,
            "details": self.details
        }

class RuntimeTimeline:
    """
    Runtime Timeline & Execution Tracker.
    Records every phase of request execution and exports in Mermaid Sequence, Mermaid Flowchart,
    JSON, Markdown, and HTML formats.
    """
    _last_timeline: List[TimelineStep] = []

    @classmethod
    def start(cls, task_type: str, capability: str) -> None:
        cls._last_timeline = []
        cls.add_step("Gateway", {"message": "Request received at AI Gateway", "task_type": task_type})
        cls.add_step("Task Analyzer", {"resolved_capability": capability})

    @classmethod
    def add_step(cls, step_name: str, details: Dict[str, Any]) -> None:
        cls._last_timeline.append(TimelineStep(step_name, details))

    @classmethod
    def get_last_timeline(cls) -> List[Dict[str, Any]]:
        return [s.to_dict() for s in cls._last_timeline]

    @classmethod
    def generate_json(cls) -> str:
        return json.dumps(cls.get_last_timeline(), indent=2)

    @classmethod
    def generate_markdown(cls) -> str:
        steps = cls.get_last_timeline()
        if not steps:
            return "# Execution Timeline\n*No execution recorded yet.*"
        lines = ["# Request Execution Timeline", ""]
        for idx, s in enumerate(steps, 1):
            lines.append(f"### {idx}. {s['step']}")
            for k, v in s["details"].items():
                lines.append(f"- **{k}**: `{v}`")
            lines.append("")
        return "\n".join(lines)

    @classmethod
    def generate_html(cls) -> str:
        steps = cls.get_last_timeline()
        rows = []
        for idx, s in enumerate(steps, 1):
            detail_str = ", ".join(f"{k}={v}" for k, v in s["details"].items())
            rows.append(f"<tr><td>{idx}</td><td>{s['step']}</td><td>{detail_str}</td></tr>")
        return f"<html><body><h1>Execution Timeline</h1><table><tr><th>#</th><th>Step</th><th>Details</th></tr>{''.join(rows)}</table></body></html>"

    @classmethod
    def generate_mermaid_sequence(cls) -> str:
        steps = cls.get_last_timeline()
        lines = ["sequenceDiagram", "    autonumber", "    actor User", "    participant Gateway", "    participant Runtime", "    participant Provider"]
        for s in steps:
            step_name = s["step"]
            if step_name == "Gateway":
                lines.append("    User->>Gateway: Send Request")
            elif step_name == "Task Analyzer":
                lines.append("    Gateway->>Runtime: Analyze Task & Capability")
            elif step_name in ("Provider Selector", "Policy Engine"):
                lines.append("    Runtime->>Runtime: Resolve Candidate Chain")
            elif step_name in ("Execution Completed", "Stream Execution"):
                p = s["details"].get("selected_provider", "Provider")
                lines.append(f"    Runtime->>{p}: Execute Generation")
                lines.append(f"    {p}-->>User: Return Unified Response")
        return "\n".join(lines)

    @classmethod
    def generate_mermaid_flowchart(cls) -> str:
        steps = cls.get_last_timeline()
        if not steps:
            return "graph TD\n    Start --> End"
        nodes = []
        for idx, s in enumerate(steps):
            node_id = f"N{idx}"
            label = s["step"].replace(" ", "_")
            nodes.append(f"    {node_id}[\"{label}\"]")
        flow = ["graph TD"] + nodes
        for i in range(len(nodes) - 1):
            flow.append(f"    N{i} --> N{i+1}")
        return "\n".join(flow)

    @classmethod
    def reset(cls) -> None:
        cls._last_timeline.clear()
