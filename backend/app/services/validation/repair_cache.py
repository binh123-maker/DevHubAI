import time
import sys
from typing import Dict, Tuple, Any, Optional

class RepairCache:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RepairCache, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._cache: Dict[Tuple[str, str], Any] = {}
        self.hits: int = 0
        self.misses: int = 0
        self.total_lookup_time: float = 0.0
        self.evictions: int = 0
        self.cached_repair_strategies: Dict[str, Any] = {}
        self._initialized = True

    @property
    def hit_ratio(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    @property
    def memory_usage(self) -> float:
        size = sys.getsizeof(self._cache)
        for val in self._cache.values():
            size += sys.getsizeof(val)
        return size / 1024.0

    def get(self, fingerprint: str, version: str) -> Optional[Any]:
        start = time.time()
        key = (fingerprint, version)
        result = self._cache.get(key)
        self.total_lookup_time += (time.time() - start)
        if result is not None:
            self.hits += 1
        else:
            self.misses += 1
        return result

    def set(self, fingerprint: str, version: str, result: Any) -> None:
        key = (fingerprint, version)
        if len(self._cache) >= 100:
            first_key = next(iter(self._cache))
            self._cache.pop(first_key, None)
            self.evictions += 1
        self._cache[key] = result

    def clear(self) -> None:
        self._cache.clear()
        self.hits = 0
        self.misses = 0
        self.total_lookup_time = 0.0
        self.evictions = 0
        self.cached_repair_strategies.clear()

    def statistics(self) -> Dict[str, Any]:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_ratio": self.hit_ratio,
            "evictions": self.evictions,
            "memory_usage": self.memory_usage,
            "repair_lookup_time": self.total_lookup_time
        }
