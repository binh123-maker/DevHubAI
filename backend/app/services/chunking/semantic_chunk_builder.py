import time
from typing import List, Optional, Any

from app.services.chunking.base_chunk_builder import BaseChunkBuilder
from app.services.chunking.rule_based_chunk_builder import RuleBasedChunkBuilder
from app.services.chunking.chunk_builder_config import ChunkBuilderConfiguration
from app.services.chunking.chunk_statistics import ChunkStatistics
from app.services.chunking.chunk_validator import ChunkValidator
from app.services.chunking.chunk_metrics import ChunkMetrics
from app.services.chunking.chunk_optimizer import ChunkOptimizer
from app.services.chunking.chunk_pipeline_context import ChunkPipelineContext
from app.services.chunking.chunk_graph import ChunkGraph

class SemanticChunkBuilder:
    def __init__(
        self,
        builder: Optional[BaseChunkBuilder] = None,
        config: Optional[ChunkBuilderConfiguration] = None,
        metrics: Optional[ChunkMetrics] = None,
        context: Optional[ChunkPipelineContext] = None
    ):
        self.config = config or ChunkBuilderConfiguration()
        self.metrics = metrics or ChunkMetrics()
        self.context = context or ChunkPipelineContext(config=self.config)
        self.builder = builder or RuleBasedChunkBuilder(config=self.config)
        self.optimizer = ChunkOptimizer(config=self.config)

    def build_chunks(
        self,
        units: List[Any],
        boundaries: List[Any]
    ) -> List[Any]:
        # Track Timers
        self.context.start_timer("builder")
        
        # 1. Delegate Building
        chunks = self.builder.build_chunks(units, boundaries, self.context)
        builder_dur = self.context.stop_timer("builder")
        
        # 2. Optimize Chunks
        self.context.start_timer("optimizer")
        chunks, opt_report = self.optimizer.optimize_chunks(chunks, self.context)
        optimizer_dur = self.context.stop_timer("optimizer")

        # 3. Validate Chunks
        self.context.start_timer("validator")
        validation_report = ChunkValidator.validate(chunks, units)
        self.context.validation = validation_report
        validator_dur = self.context.stop_timer("validator")

        # 4. Graph Construction
        if self.config.ENABLE_CHUNK_GRAPH:
            self.context.graph = ChunkGraph(chunks)

        # 5. Populate Metrics and Stats
        self.metrics.chunk_creation_time = builder_dur + optimizer_dur + validator_dur
        self.metrics.average_optimizer_time = optimizer_dur
        self.metrics.average_chunk_build_time = builder_dur
        
        # Distributions & Metadata
        if chunks:
            self.metrics.average_code_density = sum(c.quality_breakdown.get("code_density", 0.0) for c in chunks) / len(chunks)
            self.metrics.average_formula_density = sum(c.quality_breakdown.get("formula_density", 0.0) for c in chunks) / len(chunks)
            self.metrics.average_table_density = sum(c.quality_breakdown.get("table_density", 0.0) for c in chunks) / len(chunks)
            self.metrics.average_topic_consistency = sum(c.quality_breakdown.get("topic_consistency", 0.0) for c in chunks) / len(chunks)
            self.metrics.average_heading_relevance = sum(c.quality_breakdown.get("heading_relevance", 0.0) for c in chunks) / len(chunks)
            self.metrics.average_boundary_confidence = sum(c.quality_breakdown.get("boundary_confidence", 0.0) for c in chunks) / len(chunks)
            self.metrics.average_search_weight = sum(c.retrieval_weight for c in chunks) / len(chunks)

        return chunks
