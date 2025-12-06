"""
Caching system for data retrieval results.
"""

import json
import time
from typing import Any, Dict, Optional


class DataCache:
    """
    Simple in-memory cache with TTL support.

    Can be extended to use Redis, Memcached, etc.
    """

    def __init__(self, default_ttl: int = 3600, max_size: int = 1000):
        """
        Initialize cache.

        Args:
            default_ttl: Default time-to-live in seconds
            max_size: Maximum number of cached items
        """
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, float] = {}

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get item from cache.

        Args:
            key: Cache key

        Returns:
            Cached data or None if not found/expired
        """
        if key not in self._cache:
            return None

        item = self._cache[key]
        ttl = item.get("ttl", self.default_ttl)
        cached_at = item.get("cached_at", 0)

        # Check if expired
        if time.time() - cached_at > ttl:
            del self._cache[key]
            if key in self._access_times:
                del self._access_times[key]
            return None

        # Update access time for LRU
        self._access_times[key] = time.time()

        return item.get("data")

    def set(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None):
        """
        Store item in cache.

        Args:
            key: Cache key
            value: Data to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        # Evict oldest if at max size
        if len(self._cache) >= self.max_size and key not in self._cache:
            self._evict_oldest()

        ttl = ttl if ttl is not None else self.default_ttl
        self._cache[key] = {
            "data": value,
            "cached_at": time.time(),
            "ttl": ttl,
        }
        self._access_times[key] = time.time()

    def _evict_oldest(self):
        """Evict least recently used item."""
        if not self._access_times:
            return

        oldest_key = min(self._access_times.items(), key=lambda x: x[1])[0]
        del self._cache[oldest_key]
        del self._access_times[oldest_key]

    def clear(self):
        """Clear all cached items."""
        self._cache.clear()
        self._access_times.clear()

    def size(self) -> int:
        """Get current cache size."""
        return len(self._cache)

    def remove(self, key: str):
        """Remove specific item from cache."""
        if key in self._cache:
            del self._cache[key]
        if key in self._access_times:
            del self._access_times[key]

