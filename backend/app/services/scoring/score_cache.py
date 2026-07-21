import time
import sys
from typing import Dict, Tuple, Any, Optional

class ScoreCache:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ScoreCache, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._cache: Dict[Tuple[str, str, str], Any] = {}
        self.cache_hits: int = 0
        self.cache_misses: int = 0
        self.total_lookup_time: float = 0.0
        self.total_compute_time: float = 0.0
        self.cache_evictions: int = 0
        self._initialized = True

    @property
    def cache_hit_ratio(self) -> float:
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0

    @property
    def average_lookup_time(self) -> float:
        total = self.cache_hits + self.cache_misses
        return self.total_lookup_time / total if total > 0 else 0.0

    @property
    def average_compute_time(self) -> float:
        total = self.cache_hits + self.cache_misses
        return self.total_compute_time / max(1, total)

    @property
    def cache_size(self) -> int:
        return len(self._cache)

    @property
    def estimated_memory(self) -> float:
        size = sys.getsizeof(self._cache)
        for val in self._cache.values():
            size += sys.getsizeof(val)
        return size / 1024.0

    def get(self, fingerprint: str, scoring_profile_hash: str, version: str) -> Optional[Any]:
        start = time.time()
        key = (fingerprint, scoring_profile_hash, version)
        result = self._cache.get(key)
        self.total_lookup_time += (time.time() - start)
        if result is not None:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
        return result

    def set(self, fingerprint: str, scoring_profile_hash: str, version: str, score: Any, compute_time: float = 0.0) -> None:
        key = (fingerprint, scoring_profile_hash, version)
        if len(self._cache) >= 100:
            # Simple eviction
            first_key = next(iter(self._cache))
            self._cache.pop(first_key, None)
            self.cache_evictions += 1
        self._cache[key] = score
        self.total_compute_time += compute_time

    def clear(self) -> None:
        self._cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_lookup_time = 0.0
        self.total_compute_time = 0.0
        self.cache_evictions = 0

    def statistics(self) -> Dict[str, Any]:
        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_ratio": self.cache_hit_ratio,
            "hit_ratio": self.cache_hit_ratio,
            "average_lookup_time": self.average_lookup_time,
            "average_compute_time": self.average_compute_time,
            "cache_size": self.cache_size,
            "estimated_memory": self.estimated_memory,
            "cache_evictions": self.cache_evictions
        }
