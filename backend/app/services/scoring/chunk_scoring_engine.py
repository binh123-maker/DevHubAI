import time
from typing import Dict, Any, List, Optional
from app.services.chunking.semantic_chunk import SemanticChunk
from app.services.scoring.scoring_profile import ScoringProfile
from app.services.scoring.chunk_score import ChunkScore
from app.services.scoring.score_cache import ScoreCache
from app.services.scoring.score_events import ChunkScored, ChunkCacheHit, ChunkCacheMiss

class ChunkScoringEngine:
    @staticmethod
    def score_chunks(chunks: List[SemanticChunk], profile: Optional[ScoringProfile] = None) -> List[ChunkScore]:
        profile = profile or ScoringProfile()
        cache = ScoreCache()
        results: List[ChunkScore] = []
        
        for chunk in chunks:
            # Generate cache key info
            fp = getattr(chunk, "fingerprint", "")
            prof_hash = str(hash(frozenset(profile.to_dict().items())))
            ver = profile.scoring_version
            
            cached_score = cache.get(fp, prof_hash, ver)
            if cached_score:
                results.append(cached_score)
                continue
            
            # Not cached, compute score
            start = time.time()
            score = ChunkScoringEngine.score_chunk(chunk, profile)
            dur = time.time() - start
            
            # Store in cache
            cache.set(fp, prof_hash, ver, score, dur)
            results.append(score)
            
        return results

    @staticmethod
    def score_chunk(chunk: SemanticChunk, profile: ScoringProfile) -> ChunkScore:
        start_time = time.time()
        
        importance = getattr(chunk, "importance_score", 0.5)
        cohesion = chunk.quality_breakdown.get("semantic_cohesion", 0.8)
        sem_density = chunk.quality_breakdown.get("semantic_density", 0.5)
        code_density = chunk.quality_breakdown.get("code_density", 0.0)
        table_density = chunk.quality_breakdown.get("table_density", 0.0)
        formula_density = chunk.quality_breakdown.get("formula_density", 0.0)
        heading_relevance = chunk.quality_breakdown.get("heading_relevance", 0.5)
        metadata_richness = chunk.quality_breakdown.get("metadata_richness", 0.5)
        
        content = chunk.content or ""
        words = content.split()
        avg_word_len = sum(len(w) for w in words) / len(words) if words else 5.0
        readability = round(min(1.0, max(0.1, 1.0 - (avg_word_len - 4.0) / 6.0)), 2)
        
        retrieval_weight = getattr(chunk, "retrieval_weight", 1.0)
        normalized_retrieval = min(1.0, retrieval_weight / 2.0)

        weighted_sum = (
            importance * profile.importance_weight +
            cohesion * profile.cohesion_weight +
            sem_density * profile.semantic_density_weight +
            code_density * profile.code_density_weight +
            table_density * profile.table_density_weight +
            formula_density * profile.formula_density_weight +
            heading_relevance * profile.heading_relevance_weight +
            metadata_richness * profile.metadata_quality_weight +
            readability * profile.readability_weight +
            normalized_retrieval * profile.retrieval_weight
        )

        total_weights = (
            profile.importance_weight + profile.cohesion_weight + profile.semantic_density_weight +
            profile.code_density_weight + profile.table_density_weight + profile.formula_density_weight +
            profile.heading_relevance_weight + profile.metadata_quality_weight + profile.readability_weight +
            profile.retrieval_weight
        )
        base_score = weighted_sum / total_weights if total_weights > 0 else weighted_sum

        applied_rules = []
        ignored_rules = []
        bonuses = []
        penalties = []
        matched_features = []

        if heading_relevance > 0.8:
            bonuses.append({"name": "high_heading_relevance", "value": 0.05})
            applied_rules.append("HighHeadingRelevanceBonus")
        else:
            ignored_rules.append("HighHeadingRelevanceBonus")

        if code_density > 0.4:
            bonuses.append({"name": "high_code_density", "value": 0.04})
            applied_rules.append("HighCodeDensityBonus")
        else:
            ignored_rules.append("HighCodeDensityBonus")
            
        if table_density > 0.4:
            bonuses.append({"name": "high_table_density", "value": 0.04})
            applied_rules.append("HighTableDensityBonus")
        else:
            ignored_rules.append("HighTableDensityBonus")

        if len(content) < 40:
            penalties.append({"name": "short_content_penalty", "value": 0.15})
            applied_rules.append("ShortContentPenalty")
        else:
            ignored_rules.append("ShortContentPenalty")

        if avg_word_len > 10.0:
            penalties.append({"name": "excessive_word_length_penalty", "value": 0.10})
            applied_rules.append("ExcessiveWordLengthPenalty")
        else:
            ignored_rules.append("ExcessiveWordLengthPenalty")

        bonus_total = sum(b["value"] for b in bonuses)
        penalty_total = sum(p["value"] for p in penalties)
        overall_score = round(min(1.0, max(0.0, base_score + bonus_total - penalty_total)), 2)

        quality_breakdown = {
            "cohesion": cohesion,
            "semantic_density": sem_density,
            "heading_relevance": heading_relevance,
            "metadata_richness": metadata_richness,
            "readability": readability,
            "code_density": code_density,
            "table_density": table_density,
            "formula_density": formula_density
        }
        quality_score = round(sum(quality_breakdown.values()) / len(quality_breakdown), 2)

        recommended_retrieval_mode = "SEMANTIC"
        if chunk.retrieval_hints.get("contains_code"):
            recommended_retrieval_mode = "HYBRID_CODE" if code_density < 0.8 else "CODE"
        elif chunk.retrieval_hints.get("contains_table"):
            recommended_retrieval_mode = "HYBRID"
        elif metadata_richness > 0.7:
            recommended_retrieval_mode = "METADATA"
        elif readability < 0.4:
            recommended_retrieval_mode = "FULLTEXT"

        score_level = ChunkScore.determine_level(overall_score)
        
        recommendation = "GOOD_FOR_RETRIEVAL"
        if overall_score >= 0.85:
            recommendation = "HIGH_PRIORITY"
        elif overall_score < 0.40:
            recommendation = "LOW_QUALITY"
        elif cohesion < 0.5:
            recommendation = "MERGE_CANDIDATE"

        ranking_score = round(overall_score * 0.95, 2)
        ranking_priority = round(overall_score * 0.90, 2)
        retrieval_priority = round(overall_score * 0.85, 2)
        context_priority = round(overall_score * 0.88, 2)

        semantic_rank = int((1.0 - overall_score) * 10) + 1
        keyword_rank = int((1.0 - readability) * 10) + 1
        metadata_rank = int((1.0 - metadata_richness) * 10) + 1
        hybrid_rank = min(semantic_rank, keyword_rank)

        explanation = f"Chunk has an overall score of {overall_score:.2f} classified as {score_level}. Dominant factors: importance={importance:.2f}, heading_relevance={heading_relevance:.2f}."

        scoring_trace = {
            "base_score": base_score,
            "bonus_total": bonus_total,
            "penalty_total": penalty_total,
            "weighted_values": {
                "importance": importance * profile.importance_weight,
                "cohesion": cohesion * profile.cohesion_weight,
                "semantic_density": sem_density * profile.semantic_density_weight,
                "readability": readability * profile.readability_weight
            },
            "calculation_path": "weighted_average -> apply_bonuses -> apply_penalties -> min_max_clamp",
            "execution_duration_sec": time.time() - start_time
        }

        scoring_inputs = {
            "chunk_id": str(chunk.id),
            "chunk_signature": chunk.chunk_signature,
            "content_length": len(content),
            "words_count": len(words)
        }

        return ChunkScore(
            overall_score=overall_score,
            importance_score=importance,
            cohesion_score=cohesion,
            semantic_density_score=sem_density,
            readability_score=readability,
            retrieval_score=normalized_retrieval,
            code_density_score=code_density,
            table_density_score=table_density,
            formula_density_score=formula_density,
            heading_relevance_score=heading_relevance,
            metadata_quality_score=metadata_richness,
            score_signature=chunk.chunk_signature,
            score_version=profile.scoring_version,
            ranking_score=ranking_score,
            ranking_priority=ranking_priority,
            retrieval_priority=retrieval_priority,
            context_priority=context_priority,
            quality_score=quality_score,
            quality_breakdown=quality_breakdown,
            semantic_rank=semantic_rank,
            keyword_rank=keyword_rank,
            metadata_rank=metadata_rank,
            hybrid_rank=hybrid_rank,
            recommended_retrieval_mode=recommended_retrieval_mode,
            score_level=score_level,
            confidence=round(cohesion * 0.7 + sem_density * 0.3, 2),
            confidence_breakdown={"cohesion": cohesion, "density": sem_density},
            matched_features=matched_features,
            penalties=penalties,
            bonuses=bonuses,
            score_breakdown=quality_breakdown,
            explanation=explanation,
            recommendation=recommendation,
            scoring_trace=scoring_trace,
            scoring_inputs=scoring_inputs,
            applied_rules=applied_rules,
            ignored_rules=ignored_rules
        )
