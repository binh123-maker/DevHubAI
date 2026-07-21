"""
Pipeline Graph — Phase 10.6

Exports the pipeline DAG as Mermaid, Graphviz, and JSON.
Supports stage dependency graphs, execution graphs, retry/rollback graphs.
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class GraphNode:
    name: str
    label: str = ""
    status: str = "pending"   # pending | running | done | failed | skipped
    elapsed: float = 0.0


@dataclass
class GraphEdge:
    source: str
    target: str
    label: str = ""
    edge_type: str = "dependency"   # dependency | retry | rollback


@dataclass
class PipelineGraph:
    """Pipeline DAG with multiple export formats."""

    title: str = "Semantic Pipeline"
    nodes: List[GraphNode] = field(default_factory=list)
    edges: List[GraphEdge] = field(default_factory=list)

    # ------------------------------------------------------------------
    def add_node(self, name: str, label: str = "", status: str = "pending") -> None:
        self.nodes.append(GraphNode(name=name, label=label or name, status=status))

    def add_edge(self, src: str, dst: str, label: str = "", edge_type: str = "dependency") -> None:
        self.edges.append(GraphEdge(source=src, target=dst, label=label, edge_type=edge_type))

    def mark_status(self, name: str, status: str, elapsed: float = 0.0) -> None:
        for n in self.nodes:
            if n.name == name:
                n.status = status
                n.elapsed = elapsed
                return

    # ------------------------------------------------------------------
    def to_mermaid(self) -> str:
        _status_shape = {
            "pending": ("([", "])"),
            "running": ("[", "]"),
            "done": ("(", ")"),
            "failed": ("{{", "}}"),
            "skipped": ("[/", "/]"),
        }
        lines = ["graph TD"]
        for n in self.nodes:
            lp, rp = _status_shape.get(n.status, ("[", "]"))
            lines.append(f'    {n.name}{lp}"{n.label}"{rp}')
        for e in self.edges:
            arrow = "-->" if e.edge_type == "dependency" else "-.->"
            if e.label:
                lines.append(f"    {e.source} {arrow}|{e.label}| {e.target}")
            else:
                lines.append(f"    {e.source} {arrow} {e.target}")
        return "\n".join(lines)

    def to_graphviz(self) -> str:
        _color = {"done": "green", "failed": "red", "skipped": "grey", "running": "blue", "pending": "white"}
        lines = [f'digraph "{self.title}" {{', '    rankdir=TD;']
        for n in self.nodes:
            color = _color.get(n.status, "white")
            lines.append(f'    {n.name} [label="{n.label}" fillcolor={color} style=filled];')
        for e in self.edges:
            style = "dashed" if e.edge_type in ("retry", "rollback") else "solid"
            lines.append(f'    {e.source} -> {e.target} [label="{e.label}" style={style}];')
        lines.append("}")
        return "\n".join(lines)

    def to_json(self) -> str:
        return json.dumps({
            "title": self.title,
            "nodes": [{"name": n.name, "label": n.label, "status": n.status, "elapsed": n.elapsed} for n in self.nodes],
            "edges": [{"source": e.source, "target": e.target, "label": e.label, "type": e.edge_type} for e in self.edges],
        }, indent=2)

    # ------------------------------------------------------------------
    @classmethod
    def from_execution_order(cls, order: List[str], stage_results: Optional[Dict[str, Any]] = None) -> "PipelineGraph":
        g = cls()
        sr = stage_results or {}
        for name in order:
            result = sr.get(name)
            status = "pending"
            elapsed = 0.0
            if result:
                status = "done" if getattr(result, "success", True) else "failed"
                elapsed = getattr(result, "execution_time", 0.0)
            g.add_node(name, label=name, status=status)

        for i in range(len(order) - 1):
            g.add_edge(order[i], order[i + 1])
        return g
