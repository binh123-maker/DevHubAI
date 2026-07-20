from app.services.semantic.semantic_unit import SemanticUnit
from typing import Tuple

def calculate_semantic_distance(unit_a: SemanticUnit, unit_b: SemanticUnit) -> Tuple[float, float]:
    """
    Heuristic semantic distance scoring.
    Returns:
        (distance, similarity) as values between 0.0 and 1.0.
    """
    distance = 0.0

    # 1. Semantic Type change
    if unit_a.semantic_type != unit_b.semantic_type:
        distance += 0.25

    # 2. Heading Path change
    if unit_a.heading_path != unit_b.heading_path:
        distance += 0.35

    # 3. Section Path change
    if unit_a.section_path != unit_b.section_path:
        distance += 0.25

    # 4. Language change
    if unit_a.language != unit_b.language:
        distance += 0.50

    # 5. Importance difference
    importance_diff = abs(unit_a.importance_score - unit_b.importance_score)
    distance += importance_diff * 0.15

    # 6. Keyword overlap (if keywords overlap, reduce distance)
    kws_a = set(unit_a.metadata.get("keywords", []) or [])
    kws_b = set(unit_b.metadata.get("keywords", []) or [])
    if kws_a and kws_b:
        overlap = len(kws_a.intersection(kws_b))
        total_unique = len(kws_a.union(kws_b))
        jaccard = overlap / total_unique if total_unique > 0 else 0.0
        distance = max(0.0, distance - jaccard * 0.30)

    # Clamp distance
    distance = min(1.0, max(0.0, distance))
    similarity = round(1.0 - distance, 4)
    distance = round(distance, 4)

    return distance, similarity
