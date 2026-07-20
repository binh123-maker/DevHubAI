import time
from typing import List, Optional

from app.services.semantic.semantic_unit import SemanticUnit
from app.services.semantic.semantic_boundary import SemanticBoundary
from app.services.semantic.boundary_type_registry import BoundaryTypeRegistry
from app.services.semantic.boundary_metrics import BoundaryMetrics
from app.services.semantic.boundary_events import BoundaryDetected
from app.services.semantic.boundary_cache import BoundaryCache
from app.services.semantic.semantic_config import SemanticConfiguration
from app.services.semantic.semantic_pipeline_context import SemanticPipelineContext
from app.services.semantic.base_boundary_predictor import BaseBoundaryPredictor
from app.services.semantic.rule_boundary_predictor import RuleBoundaryPredictor

class SemanticBoundaryDetector:
    def __init__(
        self,
        predictor: Optional[BaseBoundaryPredictor] = None,
        registry: Optional[BoundaryTypeRegistry] = None,
        config: Optional[SemanticConfiguration] = None,
        context: Optional[SemanticPipelineContext] = None,
        metrics: Optional[BoundaryMetrics] = None,
        cache: Optional[BoundaryCache] = None
    ):
        self.registry = registry or BoundaryTypeRegistry()
        self.config = config or (context.semantic_config if context else None) or SemanticConfiguration()
        self.context = context
        self.metrics = metrics
        self.cache = cache or BoundaryCache()
        
        # Dependency Injection for the Predictor interface
        self.predictor = predictor or RuleBoundaryPredictor(registry=self.registry, config=self.config)

    def detect_boundaries(self, units: List[SemanticUnit]) -> List[SemanticBoundary]:
        """
        Scan a list of adjacent SemanticUnits and detect logical semantic boundaries.
        """
        start_time = time.time()
        
        if not units:
            return []

        # 1. Attempt to hit the cache
        semantic_hash = str(hash("".join([str(u.id) for u in units])))
        doc_version_id = str(self.context.document_version_id) if self.context and self.context.document_version_id else "default_doc"
        
        cached_result = self.cache.get(doc_version_id, semantic_hash, "v1.0")
        if cached_result is not None:
            return cached_result

        # 2. Predict boundaries using the injected predictor
        pred_start = time.time()
        boundaries = self.predictor.predict_boundaries(units, self.context)
        pred_duration = time.time() - pred_start

        # 3. Populate metrics, distributions and events
        total_conf = 0.0
        total_dist = 0.0
        
        for b in boundaries:
            total_conf += b.final_confidence
            
            # Extract distance from breakdown or metadata
            dist = b.distance_breakdown.get("distance", 0.0) if hasattr(b, "distance_breakdown") and b.distance_breakdown else 0.0
            total_dist += dist

            # Record in metrics
            self._record_metrics(b)
            self._emit_event(b)

        # 4. Finalize overall metrics
        proc_duration = time.time() - start_time
        if self.metrics:
            self.metrics.total_boundaries = len(boundaries)
            self.metrics.processing_time = proc_duration
            if len(units) > 0:
                self.metrics.boundary_density = len(boundaries) / len(units)
            if boundaries:
                self.metrics.average_confidence = total_conf / len(boundaries)
                self.metrics.average_distance = total_dist / max(1, len(boundaries) - 1)
                
            # Copy hit distributions from predictor if available
            if hasattr(self.predictor, "rules"):
                # Populate rule hit metrics and timing
                for rname in self.metrics.rule_hit_distribution.keys():
                    if rname not in self.metrics.execution_time_per_rule:
                        self.metrics.execution_time_per_rule[rname] = pred_duration / len(boundaries)

        # 5. Populate cache
        self.cache.set(doc_version_id, semantic_hash, "v1.0", boundaries)

        return boundaries

    def _record_metrics(self, boundary: SemanticBoundary):
        if not self.metrics:
            return
        b_type = boundary.boundary_type
        if b_type == "HEADING_BREAK":
            self.metrics.heading_boundaries += 1
        elif b_type == "SECTION_BREAK":
            self.metrics.section_boundaries += 1
        elif b_type == "TOPIC_SHIFT":
            self.metrics.topic_shift_boundaries += 1
        elif b_type in ("CODE_START", "CODE_END"):
            self.metrics.code_boundaries += 1
        elif b_type in ("TABLE_START", "TABLE_END"):
            self.metrics.table_boundaries += 1
        elif b_type in ("FORMULA_START", "FORMULA_END"):
            self.metrics.formula_boundaries += 1

        # Populate type distribution
        if b_type not in self.metrics.boundary_distribution:
            self.metrics.boundary_distribution[b_type] = 0
        self.metrics.boundary_distribution[b_type] += 1

        # Populate rule hit distribution
        for rule in boundary.matched_rules:
            if rule not in self.metrics.rule_hit_distribution:
                self.metrics.rule_hit_distribution[rule] = 0
            self.metrics.rule_hit_distribution[rule] += 1

    def _emit_event(self, boundary: SemanticBoundary):
        if self.context:
            event = BoundaryDetected(
                boundary_id=boundary.id,
                boundary_type=boundary.boundary_type,
                details=boundary.reason
            )
            if not hasattr(self.context, "boundary_events"):
                self.context.boundary_events = []
            self.context.boundary_events.append(event)
