import time
import uuid
from typing import Any, Dict, List, Optional
from app.services.semantic.semantic_unit import SemanticUnit
from app.services.semantic.semantic_classifier import SemanticContextWindow
from app.services.semantic.base_classifier import BaseSemanticClassifier
from app.services.semantic.rule_based_classifier import RuleBasedSemanticClassifier
from app.services.semantic.semantic_config import SemanticConfiguration
from app.services.semantic.semantic_pipeline_context import SemanticPipelineContext
from app.services.semantic.semantic_metrics import SemanticMetrics
from app.services.semantic.classification_trace import ClassificationTrace
from app.services.semantic.semantic_events import SemanticDetected

class SemanticRelationshipBuilder:
    @staticmethod
    def build_relationships(units: List[SemanticUnit], nodes: List[Any]) -> None:
        """
        Populate previous_unit_id, next_unit_id, and parent_heading_id relationships.
        """
        if not units:
            return

        # 1. Bidirectional sequence links
        for i, unit in enumerate(units):
            if i > 0:
                unit.previous_unit_id = units[i - 1].id
            if i < len(units) - 1:
                unit.next_unit_id = units[i + 1].id

        # 2. Map structure nodes
        node_map = {}
        for n in nodes:
            nid = getattr(n, "id", None) if not isinstance(n, dict) else n.get("id")
            if nid:
                node_map[nid] = n

        # Map to quickly find SemanticUnits by structure_node_id
        unit_by_node_id = {u.structure_node_id: u for u in units}

        # 3. Heading hierarchy resolution
        for unit in units:
            node = node_map.get(unit.structure_node_id)
            if not node:
                continue
            
            parent_id = getattr(node, "parent_id", None) if not isinstance(node, dict) else node.get("parent_id")
            
            # Find nearest ancestor that is a heading
            curr_parent_id = parent_id
            while curr_parent_id:
                p_node = node_map.get(curr_parent_id)
                if not p_node:
                    break
                p_type = getattr(p_node, "node_type", "") if not isinstance(p_node, dict) else p_node.get("node_type", "")
                
                if "heading" in str(p_type).lower():
                    p_unit = unit_by_node_id.get(curr_parent_id)
                    if p_unit:
                        unit.parent_heading_id = p_unit.id
                        break
                
                # Traverse up
                curr_parent_id = getattr(p_node, "parent_id", None) if not isinstance(p_node, dict) else p_node.get("parent_id")


class SemanticUnitDetector:
    def __init__(
        self,
        classifier: Optional[BaseSemanticClassifier] = None,
        config: Optional[SemanticConfiguration] = None,
        context: Optional[SemanticPipelineContext] = None,
        metrics: Optional[SemanticMetrics] = None
    ):
        self.context = context
        self.metrics = metrics
        self.config = config or (context.semantic_config if context else None) or SemanticConfiguration()
        self.classifier = classifier or RuleBasedSemanticClassifier(config=self.config)

    def _get_attr(self, obj: Any, attr: str, default: Any = None) -> Any:
        if isinstance(obj, dict):
            return obj.get(attr, default)
        return getattr(obj, attr, default)

    def _get_metadata(self, obj: Any, key: str, default: Any = None) -> Any:
        meta = self._get_attr(obj, "metadata_json", {}) or {}
        return meta.get(key, default)

    def detect_semantic_units(self, nodes: Optional[List[Any]] = None) -> List[SemanticUnit]:
        """
        Main entry point to scan structure nodes and output Semantic Units.
        """
        proc_start = time.time()
        
        # If nodes is not passed, fetch from pipeline context
        if nodes is None:
            if self.context:
                nodes = self.context.structure_nodes
            else:
                nodes = []

        units: List[SemanticUnit] = []
        if not nodes:
            return units

        # Build parent heading lookup
        node_map = {}
        for n in nodes:
            nid = self._get_attr(n, "id")
            if nid:
                node_map[nid] = n

        total_conf = 0.0
        total_imp = 0.0
        total_class_time = 0.0

        # Process each node
        for i, node in enumerate(nodes):
            # Resolve parent heading node
            parent_id = self._get_attr(node, "parent_id")
            parent_heading_node = None
            curr_parent_id = parent_id
            while curr_parent_id:
                p_node = node_map.get(curr_parent_id)
                if not p_node:
                    break
                p_type = self._get_attr(p_node, "node_type", "")
                if "heading" in str(p_type).lower():
                    parent_heading_node = p_node
                    break
                curr_parent_id = self._get_attr(p_node, "parent_id")

            # Extract window neighbors
            prev_node = nodes[i - 1] if i > 0 else None
            next_node = nodes[i + 1] if i < len(nodes) - 1 else None

            # Construct SemanticContextWindow
            context_window = SemanticContextWindow(
                current_node=node,
                previous_node=prev_node,
                next_node=next_node,
                parent_heading=parent_heading_node,
                section=None
            )

            # Classify using pluggable classifier interface
            class_start = time.time()
            if hasattr(self.classifier, "classify_with_trace") and self.config.ENABLE_TRACE:
                semantic_type, confidence, importance, trace = self.classifier.classify_with_trace(context_window)
            else:
                semantic_type, base_conf = self.classifier.classify(context_window)
                confidence = self.classifier.calculate_confidence(context_window, semantic_type, base_conf)
                content = self._get_attr(node, "content_text", "") or ""
                importance = self.classifier.calculate_importance(semantic_type, content)
                trace = None
            
            class_duration = time.time() - class_start
            total_class_time += class_duration

            # Token estimation (from node metadata or calculated fallback)
            est_tokens = self._get_metadata(node, "token_estimate", None)
            if est_tokens is None:
                content = self._get_attr(node, "content_text", "") or ""
                est_tokens = max(1, len(content) // 4)

            # Retrieve paths
            heading_path = self._get_metadata(node, "heading_path", [])
            section_path = self._get_metadata(node, "section_path", [])
            document_path = self._get_metadata(node, "document_path", [])

            # Create SemanticUnit
            unit_id = uuid.uuid4()
            unit = SemanticUnit(
                id=unit_id,
                structure_node_id=self._get_attr(node, "id"),
                semantic_type=semantic_type,
                content=self._get_attr(node, "content_text", "") or "",
                language=self._get_attr(node, "language") or self._get_metadata(node, "language", "en"),
                semantic_confidence=confidence,
                importance_score=importance,
                estimated_tokens=est_tokens,
                heading_path=heading_path,
                section_path=section_path,
                document_path=document_path,
                page_start=self._get_attr(node, "page_start"),
                page_end=self._get_attr(node, "page_end"),
                line_start=self._get_attr(node, "line_start"),
                line_end=self._get_attr(node, "line_end"),
                char_start=self._get_attr(node, "char_start"),
                char_end=self._get_attr(node, "char_end"),
                metadata=self._get_attr(node, "metadata_json", {}) or {}
            )
            units.append(unit)

            # Store trace if tracing is enabled and context is active
            if trace and self.context and self.context.tracing_enabled:
                self.context.traces[unit_id] = trace

            # Emit events if context is active
            if self.context:
                ev = SemanticDetected(
                    semantic_unit_id=unit_id,
                    document_version_id=self.context.document_version_id or uuid.uuid4(),
                    details=f"Detected unit of type '{semantic_type}'"
                )
                self.context.events.append(ev)

            # Accumulate values
            total_conf += confidence
            total_imp += importance

            # Record in metrics
            if self.metrics:
                self.metrics.total_units += 1
                if semantic_type in self.metrics.semantic_distribution:
                    self.metrics.semantic_distribution[semantic_type] += 1

        # Build relations (Part 5)
        if self.config.ENABLE_RELATIONSHIPS:
            SemanticRelationshipBuilder.build_relationships(units, nodes)

        proc_duration = time.time() - proc_start

        # Record metrics summary
        if self.metrics:
            self.metrics.total_nodes = len(nodes)
            self.metrics.processing_time = proc_duration
            self.metrics.classification_time = total_class_time
            if units:
                self.metrics.average_confidence = total_conf / len(units)
                self.metrics.average_importance = total_imp / len(units)

        # Store in context if active
        if self.context:
            self.context.semantic_units = units
            self.context.end_timer()

        return units
