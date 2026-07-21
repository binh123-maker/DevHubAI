import time
import uuid
from typing import List, Optional, Any, Dict
from app.services.chunking.base_chunk_builder import BaseChunkBuilder
from app.services.chunking.semantic_chunk import SemanticChunk
from app.services.chunking.chunk_intelligence import ChunkIntelligenceAnalyzer
from app.services.chunking.chunk_builder_config import ChunkBuilderConfiguration

class RuleBasedChunkBuilder(BaseChunkBuilder):
    def __init__(
        self,
        config: Optional[ChunkBuilderConfiguration] = None
    ):
        self.config = config or ChunkBuilderConfiguration()

    def supports(self, document_type: str) -> bool:
        return True

    def build_chunks(
        self,
        units: List[Any],
        boundaries: List[Any],
        context: Optional[Any] = None
    ) -> List[SemanticChunk]:
        if not units:
            return []

        boundary_map: Dict[Optional[uuid.UUID], Any] = {}
        for b in boundaries:
            boundary_map[b.previous_unit_id] = b

        draft_chunks: List[List[Any]] = []
        current_group: List[Any] = []
        accumulated_tokens = 0

        def estimate_unit_tokens(u: Any) -> int:
            return int(len(u.content.split()) * 1.35)

        for i, unit in enumerate(units):
            unit_tokens = estimate_unit_tokens(unit)
            should_split = False
            
            if current_group:
                prev_unit = current_group[-1]
                boundary = boundary_map.get(prev_unit.id)
                
                if prev_unit.heading_path != unit.heading_path:
                    should_split = True
                elif prev_unit.section_path != unit.section_path:
                    should_split = True
                elif boundary and self.config.ENABLE_BOUNDARY_SPLIT and boundary.chunk_recommendation == "split":
                    should_split = True
                elif accumulated_tokens + unit_tokens > self.config.DEFAULT_MAX_TOKENS:
                    should_split = True

            if should_split and current_group:
                draft_chunks.append(current_group)
                current_group = []
                accumulated_tokens = 0

            current_group.append(unit)
            accumulated_tokens += unit_tokens

        if current_group:
            draft_chunks.append(current_group)

        # Merge Chunks
        draft_chunks = self._merge_drafts(draft_chunks, boundary_map, context)

        # Split Chunks
        draft_chunks = self._split_drafts(draft_chunks, context)

        # Convert to SemanticChunk objects
        chunks: List[SemanticChunk] = []
        doc_version_id = units[0].structure_node_id
        workspace_id = context.workspace_id if context else None
        
        for idx, chunk_units in enumerate(draft_chunks):
            content = " ".join([u.content for u in chunk_units])
            words_count = len(content.split())
            chars_count = len(content)
            tokens_count = sum(estimate_unit_tokens(u) for u in chunk_units)
            
            heading_path = chunk_units[0].heading_path
            section_path = chunk_units[0].section_path
            document_path = chunk_units[0].document_path if hasattr(chunk_units[0], "document_path") else []
            language = chunk_units[0].language

            importance_score = max([u.importance_score for u in chunk_units if u.importance_score is not None], default=0.5)
            
            chunk_boundaries = []
            for u in chunk_units[:-1]:
                b = boundary_map.get(u.id)
                if b:
                    chunk_boundaries.append(b)

            metadata_snapshot = {}
            for u in chunk_units:
                if hasattr(u, "metadata") and u.metadata:
                    metadata_snapshot.update(u.metadata)

            code_density = ChunkIntelligenceAnalyzer.calculate_code_density(chunk_units)
            formula_density = ChunkIntelligenceAnalyzer.calculate_formula_density(chunk_units)
            table_density = ChunkIntelligenceAnalyzer.calculate_table_density(chunk_units)
            heading_relevance = ChunkIntelligenceAnalyzer.calculate_heading_relevance(heading_path, content)
            boundary_confidence = ChunkIntelligenceAnalyzer.calculate_boundary_confidence(chunk_boundaries)
            
            semantic_density = round(min(1.0, tokens_count / max(1, chars_count) * 4.0), 2)
            semantic_cohesion = round(sum(u.semantic_confidence for u in chunk_units) / len(chunk_units), 2)
            topic_consistency = round(1.0 - (code_density * 0.2 + table_density * 0.2), 2)
            metadata_richness = round(min(1.0, len(metadata_snapshot.keys()) / 8.0), 2)
            
            quality_breakdown = {
                "semantic_density": semantic_density,
                "semantic_cohesion": semantic_cohesion,
                "topic_consistency": topic_consistency,
                "heading_relevance": heading_relevance,
                "metadata_richness": metadata_richness,
                "boundary_confidence": boundary_confidence,
                "code_density": code_density,
                "table_density": table_density,
                "formula_density": formula_density
            }
            
            quality_score = ChunkIntelligenceAnalyzer.calculate_chunk_quality(quality_breakdown)
            retrieval_weight = ChunkIntelligenceAnalyzer.calculate_retrieval_weight(importance_score, code_density, table_density)
            
            retrieval_hints = ChunkIntelligenceAnalyzer.generate_retrieval_hints(chunk_units)
            recommended_search_modes = ChunkIntelligenceAnalyzer.detect_search_modes(retrieval_hints)
            
            generated_units = [str(u.id) for u in chunk_units]
            generated_boundaries = [str(b.id) for b in chunk_boundaries]
            source_nodes = [str(u.structure_node_id) for u in chunk_units]
            
            overlap_before = ""
            overlap_after = ""
            if self.config.ENABLE_OVERLAP:
                if idx > 0:
                    prev_units = draft_chunks[idx - 1]
                    prev_content = " ".join([u.content for u in prev_units])
                    overlap_before = prev_content[-self.config.MAX_OVERLAP:] if len(prev_content) > self.config.MAX_OVERLAP else prev_content
                if idx < len(draft_chunks) - 1:
                    nxt_units = draft_chunks[idx + 1]
                    nxt_content = " ".join([u.content for u in nxt_units])
                    overlap_after = nxt_content[:self.config.MAX_OVERLAP] if len(nxt_content) > self.config.MAX_OVERLAP else nxt_content

            chunk = SemanticChunk(
                id=uuid.uuid4(),
                document_version_id=doc_version_id,
                workspace_id=workspace_id,
                chunk_index=idx,
                semantic_units=chunk_units,
                semantic_boundaries=chunk_boundaries,
                content=content,
                language=language,
                heading_path=heading_path,
                section_path=section_path,
                document_path=document_path,
                metadata_snapshot=metadata_snapshot,
                importance_score=importance_score,
                retrieval_weight=retrieval_weight,
                quality_score=quality_score,
                quality_breakdown=quality_breakdown,
                retrieval_hints=retrieval_hints,
                recommended_search_modes=recommended_search_modes,
                estimated_tokens=tokens_count,
                estimated_words=words_count,
                estimated_characters=chars_count,
                overlap_before=overlap_before,
                overlap_after=overlap_after,
                generated_from_units=generated_units,
                generated_from_boundaries=generated_boundaries,
                generated_from_headings=heading_path,
                generated_from_sections=section_path,
                source_metadata=metadata_snapshot,
                source_structure_nodes=source_nodes,
                source_boundary_ids=generated_boundaries,
                creation_reason="Sequential Semantic Boundary Accumulation",
                creation_trace={
                    "rule_configuration": self.config.__dict__,
                    "units_processed": len(chunk_units)
                }
            )
            chunks.append(chunk)
            
        return chunks

    def _merge_drafts(self, draft_chunks: List[List[Any]], boundary_map: Dict[Optional[uuid.UUID], Any], context: Optional[Any]) -> List[List[Any]]:
        if not self.config.ENABLE_MERGE_SMALL_CHUNKS:
            return draft_chunks
            
        def estimate_unit_tokens(u: Any) -> int:
            return int(len(u.content.split()) * 1.35)

        i = 0
        while i < len(draft_chunks) - 1:
            chunk_a = draft_chunks[i]
            chunk_b = draft_chunks[i + 1]
            
            tokens_a = sum(estimate_unit_tokens(u) for u in chunk_a)
            tokens_b = sum(estimate_unit_tokens(u) for u in chunk_b)
            
            boundary = boundary_map.get(chunk_a[-1].id)
            allow_merge = True
            if boundary and boundary.chunk_recommendation == "split":
                allow_merge = False
            
            same_heading = chunk_a[-1].heading_path == chunk_b[0].heading_path
            
            if allow_merge and same_heading and (tokens_a < self.config.DEFAULT_MIN_TOKENS or tokens_a + tokens_b <= self.config.DEFAULT_MAX_TOKENS):
                draft_chunks[i] = chunk_a + chunk_b
                draft_chunks.pop(i + 1)
                if context and hasattr(context, "statistics"):
                    context.statistics.merge_count += 1
            else:
                i += 1
        return draft_chunks

    def _split_drafts(self, draft_chunks: List[List[Any]], context: Optional[Any]) -> List[List[Any]]:
        if not self.config.ENABLE_SPLIT_LARGE_CHUNKS:
            return draft_chunks

        def estimate_unit_tokens(u: Any) -> int:
            return int(len(u.content.split()) * 1.35)

        i = 0
        while i < len(draft_chunks):
            chunk_units = draft_chunks[i]
            tokens = sum(estimate_unit_tokens(u) for u in chunk_units)
            if tokens > self.config.DEFAULT_MAX_TOKENS and len(chunk_units) > 1:
                mid = len(chunk_units) // 2
                draft_chunks[i] = chunk_units[:mid]
                draft_chunks.insert(i + 1, chunk_units[mid:])
                if context and hasattr(context, "statistics"):
                    context.statistics.split_count += 1
            else:
                i += 1
        return draft_chunks

    # Base class stub overrides
    def merge_chunks(self, chunks: List[Any], context: Optional[Any] = None) -> List[Any]:
        return chunks
    def split_chunks(self, chunks: List[Any], context: Optional[Any] = None) -> List[Any]:
        return chunks
    def optimize_chunks(self, chunks: List[Any], context: Optional[Any] = None) -> List[Any]:
        return chunks
    def validate_chunks(self, chunks: List[Any], context: Optional[Any] = None) -> Any:
        return None
