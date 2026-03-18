"""TTL Cache - Time-based caching decorator for function results."""

import functools
import logging
import threading
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Tuple

logger = logging.getLogger(__name__)


class TTLCache:
    """Function result cache with time-to-live expiration"""

    def __init__(self, ttl_minutes: int = 5) -> None:
        self._ttl = timedelta(minutes=ttl_minutes)
        self._cache: Dict[Any, Tuple[Any, datetime]] = {}
        self._hits = 0
        self._misses = 0
        self._lock = threading.RLock()

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """Wrap function with caching"""

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                key = (args, tuple(sorted(kwargs.items())))
            except TypeError:
                return func(*args, **kwargs)

            with self._lock:
                if key in self._cache:
                    result, timestamp = self._cache[key]
                    if datetime.now() - timestamp < self._ttl:
                        self._hits += 1
                        return result
                    else:
                        del self._cache[key]

            result = func(*args, **kwargs)

            with self._lock:
                self._cache[key] = (result, datetime.now())
                self._misses += 1

            return result

        wrapper.cache_clear = self.clear  # type: ignore[attr-defined]
        wrapper.cache_stats = self.stats  # type: ignore[attr-defined]
        return wrapper

    def clear(self) -> None:
        """Clear cache"""
        with self._lock:
            self._cache.clear()

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total * 100) if total > 0 else 0
            return {"hits": self._hits, "misses": self._misses, "hit_rate": f"{hit_rate:.1f}%"}


def cached(ttl_minutes: int = 5) -> TTLCache:
    """Decorator factory for caching"""
    return TTLCache(ttl_minutes=ttl_minutes)
