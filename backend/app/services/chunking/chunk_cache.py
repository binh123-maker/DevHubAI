import time
import sys
from typing import Any, Dict, Optional, Tuple

class ChunkCache:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ChunkCache, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._cache: Dict[Tuple[str, str], Any] = {}
        self.cache_hits: int = 0
        self.cache_misses: int = 0
        self.total_lookup_time: float = 0.0
        self.total_build_time: float = 0.0
        self.eviction_count: int = 0
        self._initialized = True

    @property
    def hit_ratio(self) -> float:
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0

    @property
    def average_lookup_time(self) -> float:
        total = self.cache_hits + self.cache_misses
        return self.total_lookup_time / total if total > 0 else 0.0

    @property
    def average_build_time(self) -> float:
        total = self.cache_hits + self.cache_misses
        return self.total_build_time / total if total > 0 else 0.0

    @property
    def cache_size(self) -> int:
        return len(self._cache)

    @property
    def cache_memory_usage(self) -> float:
        # Approximate size of elements in KB
        size = sys.getsizeof(self._cache)
        for val in self._cache.values():
            size += sys.getsizeof(val)
        return size / 1024.0

    def get(self, document_version_id: str, semantic_hash: str) -> Optional[Any]:
        start = time.time()
        key = (document_version_id, semantic_hash)
        result = self._cache.get(key)
        
        lookup_duration = time.time() - start
        self.total_lookup_time += lookup_duration
        
        if result is not None:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
            
        return result

    def set(self, document_version_id: str, semantic_hash: str, chunks: Any) -> None:
        key = (document_version_id, semantic_hash)
        # Simple LRU limit eviction stub
        if len(self._cache) >= 50:
            # Evict first element
            first_key = next(iter(self._cache))
            self._cache.pop(first_key, None)
            self.eviction_count += 1
        self._cache[key] = chunks

    def clear(self) -> None:
        self._cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_lookup_time = 0.0
        self.total_build_time = 0.0
        self.eviction_count = 0

    def statistics(self) -> Dict[str, Any]:
        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_ratio": self.hit_ratio,
            "average_lookup_time": self.average_lookup_time,
            "average_build_time": self.average_build_time,
            "cache_size": self.cache_size,
            "eviction_count": self.eviction_count,
            "cache_memory_usage": self.cache_memory_usage
        }
