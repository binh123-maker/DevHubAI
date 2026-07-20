import time
from typing import Any, Dict, Optional, Tuple

class BoundaryCache:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(BoundaryCache, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._cache: Dict[Tuple[str, str, str], Any] = {}
        self.cache_hits: int = 0
        self.cache_misses: int = 0
        self.total_lookup_time: float = 0.0
        self._initialized = True

    @property
    def hit_ratio(self) -> float:
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0

    @property
    def average_lookup_time(self) -> float:
        total = self.cache_hits + self.cache_misses
        return self.total_lookup_time / total if total > 0 else 0.0

    def get(self, document_version_id: str, semantic_hash: str, classifier_version: str) -> Optional[Any]:
        start = time.time()
        key = (document_version_id, semantic_hash, classifier_version)
        result = self._cache.get(key)
        
        lookup_duration = time.time() - start
        self.total_lookup_time += lookup_duration
        
        if result is not None:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
            
        return result

    def set(self, document_version_id: str, semantic_hash: str, classifier_version: str, boundaries: Any) -> None:
        key = (document_version_id, semantic_hash, classifier_version)
        self._cache[key] = boundaries

    def delete(self, document_version_id: str, semantic_hash: str, classifier_version: str) -> None:
        key = (document_version_id, semantic_hash, classifier_version)
        self._cache.pop(key, None)

    def clear(self) -> None:
        self._cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_lookup_time = 0.0
