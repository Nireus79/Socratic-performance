"""
TTL-based caching system.
"""

import logging
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class TTLCache:
    """
    Time-to-live (TTL) based cache.

    Automatically expires entries after a configured TTL.
    Useful for caching database queries, API responses, etc.
    """

    def __init__(self, ttl_minutes: int = 30):
        """
        Initialize the cache.

        Args:
            ttl_minutes: Time-to-live for cache entries in minutes
        """
        self.ttl_seconds = ttl_minutes * 60
        self._cache: Dict[str, tuple[Any, float]] = {}
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if expired/missing
        """
        if key not in self._cache:
            self._misses += 1
            return None

        value, timestamp = self._cache[key]

        # Check if expired
        if time.time() - timestamp > self.ttl_seconds:
            del self._cache[key]
            self._misses += 1
            logger.debug(f"Cache entry {key} expired")
            return None

        self._hits += 1
        logger.debug(f"Cache hit for {key}")
        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set a cache entry.

        Args:
            key: Cache key
            value: Value to cache
        """
        self._cache[key] = (value, time.time())
        logger.debug(f"Cached {key}")

    def delete(self, key: str) -> bool:
        """
        Delete a cache entry.

        Args:
            key: Cache key

        Returns:
            True if entry was deleted
        """
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Deleted cache entry {key}")
            return True
        return False

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache = {}
        logger.info("Cleared cache")

    def stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Statistics dictionary with hits, misses, etc.
        """
        total = self._hits + self._misses
        hit_ratio = (self._hits / total * 100) if total > 0 else 0

        return {
            "entries": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "total_requests": total,
            "hit_ratio": hit_ratio,
            "ttl_seconds": self.ttl_seconds,
        }

    def cleanup_expired(self) -> int:
        """
        Remove expired entries.

        Returns:
            Number of entries removed
        """
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self._cache.items()
            if current_time - timestamp > self.ttl_seconds
        ]

        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

        return len(expired_keys)

    def get_entry_age(self, key: str) -> Optional[float]:
        """
        Get the age of a cache entry in seconds.

        Args:
            key: Cache key

        Returns:
            Age in seconds or None if not in cache
        """
        if key not in self._cache:
            return None

        _, timestamp = self._cache[key]
        return time.time() - timestamp
