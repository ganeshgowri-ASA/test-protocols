"""
Caching Layer for Railway Production Deployment
================================================
Enterprise-grade caching with multiple backends,
TTL management, and cache invalidation.
"""

import os
import time
import threading
import hashlib
import json
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, Callable, TypeVar
from functools import wraps
from collections import OrderedDict
from dataclasses import dataclass


T = TypeVar('T')


class CacheConfig:
    """Cache configuration from environment"""

    def __init__(self):
        self.default_ttl = int(os.getenv("CACHE_DEFAULT_TTL", "300"))  # 5 minutes
        self.max_size = int(os.getenv("CACHE_MAX_SIZE", "1000"))
        self.enable_stats = os.getenv("CACHE_ENABLE_STATS", "true").lower() == "true"


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    value: Any
    created_at: float
    expires_at: float
    hits: int = 0
    last_accessed: float = None

    def __post_init__(self):
        self.last_accessed = self.created_at

    def is_expired(self) -> bool:
        return time.time() > self.expires_at

    def access(self):
        self.hits += 1
        self.last_accessed = time.time()


class LRUCache:
    """
    Thread-safe LRU cache implementation.

    Features:
    - Least Recently Used eviction
    - TTL support per entry
    - Cache statistics
    - Automatic cleanup
    """

    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "expirations": 0
        }

        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                self._stats["misses"] += 1
                return default

            if entry.is_expired():
                del self._cache[key]
                self._stats["expirations"] += 1
                self._stats["misses"] += 1
                return default

            # Move to end (most recently used)
            self._cache.move_to_end(key)
            entry.access()
            self._stats["hits"] += 1

            return entry.value

    def set(self, key: str, value: Any, ttl: int = None) -> None:
        """Set value in cache"""
        ttl = ttl or self.default_ttl
        now = time.time()

        with self._lock:
            # Remove oldest if at capacity
            while len(self._cache) >= self.max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                self._stats["evictions"] += 1

            self._cache[key] = CacheEntry(
                value=value,
                created_at=now,
                expires_at=now + ttl
            )

    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()

    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired"""
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return False
            if entry.is_expired():
                del self._cache[key]
                self._stats["expirations"] += 1
                return False
            return True

    def get_or_set(self, key: str, factory: Callable[[], T], ttl: int = None) -> T:
        """Get value or compute and store it"""
        value = self.get(key)
        if value is not None:
            return value

        value = factory()
        self.set(key, value, ttl)
        return value

    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching a pattern"""
        count = 0
        with self._lock:
            keys_to_delete = [
                k for k in self._cache.keys()
                if pattern in k
            ]
            for key in keys_to_delete:
                del self._cache[key]
                count += 1
        return count

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total = self._stats["hits"] + self._stats["misses"]
            hit_rate = self._stats["hits"] / total if total > 0 else 0

            return {
                **self._stats,
                "size": len(self._cache),
                "max_size": self.max_size,
                "hit_rate": round(hit_rate * 100, 2)
            }

    def reset_stats(self) -> None:
        """Reset cache statistics"""
        with self._lock:
            self._stats = {
                "hits": 0,
                "misses": 0,
                "evictions": 0,
                "expirations": 0
            }

    def _cleanup_loop(self):
        """Periodically clean up expired entries"""
        while True:
            time.sleep(60)  # Cleanup every minute
            self._cleanup_expired()

    def _cleanup_expired(self):
        """Remove all expired entries"""
        with self._lock:
            expired_keys = [
                k for k, v in self._cache.items()
                if v.is_expired()
            ]
            for key in expired_keys:
                del self._cache[key]
                self._stats["expirations"] += 1


class CacheManager:
    """
    Multi-namespace cache manager.

    Provides separate caches for different purposes
    with unified interface.
    """

    def __init__(self, config: CacheConfig = None):
        self.config = config or CacheConfig()
        self._caches: Dict[str, LRUCache] = {}
        self._lock = threading.Lock()

    def get_cache(self, namespace: str = "default") -> LRUCache:
        """Get or create a cache for a namespace"""
        with self._lock:
            if namespace not in self._caches:
                self._caches[namespace] = LRUCache(
                    max_size=self.config.max_size,
                    default_ttl=self.config.default_ttl
                )
            return self._caches[namespace]

    def get(self, key: str, namespace: str = "default", default: Any = None) -> Any:
        """Get value from cache"""
        return self.get_cache(namespace).get(key, default)

    def set(self, key: str, value: Any, namespace: str = "default", ttl: int = None) -> None:
        """Set value in cache"""
        self.get_cache(namespace).set(key, value, ttl)

    def delete(self, key: str, namespace: str = "default") -> bool:
        """Delete value from cache"""
        return self.get_cache(namespace).delete(key)

    def clear(self, namespace: str = None) -> None:
        """Clear cache(s)"""
        with self._lock:
            if namespace:
                if namespace in self._caches:
                    self._caches[namespace].clear()
            else:
                for cache in self._caches.values():
                    cache.clear()

    def get_all_stats(self) -> Dict[str, Dict]:
        """Get stats for all caches"""
        with self._lock:
            return {
                namespace: cache.get_stats()
                for namespace, cache in self._caches.items()
            }


# Caching decorators
def cached(ttl: int = None, key_prefix: str = None, namespace: str = "default"):
    """
    Decorator to cache function results.

    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
        namespace: Cache namespace
    """
    cache = cache_manager.get_cache(namespace)

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [key_prefix or func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()

            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result

            # Compute and cache
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        # Add cache control methods
        wrapper.cache_clear = lambda: cache.invalidate_pattern(key_prefix or func.__name__)
        wrapper.cache_info = lambda: cache.get_stats()

        return wrapper
    return decorator


def cached_property(ttl: int = None, namespace: str = "properties"):
    """
    Decorator for cached class properties.

    Args:
        ttl: Time to live in seconds
        namespace: Cache namespace
    """
    cache = cache_manager.get_cache(namespace)

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(self):
            cache_key = f"{type(self).__name__}:{id(self)}:{func.__name__}"

            result = cache.get(cache_key)
            if result is not None:
                return result

            result = func(self)
            cache.set(cache_key, result, ttl)
            return result

        return property(wrapper)
    return decorator


# Query result caching
class QueryCache:
    """Specialized cache for database query results"""

    def __init__(self, cache: LRUCache = None):
        self.cache = cache or cache_manager.get_cache("queries")

    def cache_query(self, query_hash: str, result: Any, ttl: int = 60):
        """Cache a query result"""
        self.cache.set(f"query:{query_hash}", result, ttl)

    def get_cached_query(self, query_hash: str) -> Optional[Any]:
        """Get cached query result"""
        return self.cache.get(f"query:{query_hash}")

    def invalidate_table(self, table_name: str):
        """Invalidate all cached queries for a table"""
        self.cache.invalidate_pattern(f"query:{table_name}")

    @staticmethod
    def hash_query(query: str, params: tuple = None) -> str:
        """Generate hash for a query"""
        key = query + str(params or "")
        return hashlib.md5(key.encode()).hexdigest()


# Session data cache
class SessionCache:
    """Specialized cache for session data"""

    def __init__(self):
        self.cache = cache_manager.get_cache("sessions")
        self.default_ttl = 3600  # 1 hour

    def get_session_data(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        return self.cache.get(f"session:{session_id}")

    def set_session_data(self, session_id: str, data: Dict, ttl: int = None):
        """Store session data"""
        self.cache.set(f"session:{session_id}", data, ttl or self.default_ttl)

    def update_session_data(self, session_id: str, updates: Dict):
        """Update session data"""
        data = self.get_session_data(session_id) or {}
        data.update(updates)
        self.set_session_data(session_id, data)

    def delete_session(self, session_id: str):
        """Delete session data"""
        self.cache.delete(f"session:{session_id}")


# Global cache manager instance
cache_manager = CacheManager()
query_cache = QueryCache()
session_cache = SessionCache()


# Streamlit-specific caching integration
def streamlit_cached(ttl: int = 300, show_spinner: bool = True):
    """
    Enhanced caching decorator for Streamlit.

    Combines Streamlit's caching with our custom cache for better control.
    """
    def decorator(func: Callable):
        # Use our cache for control
        cache = cache_manager.get_cache("streamlit")

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate key
            key_parts = [func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()

            # Check cache
            result = cache.get(cache_key)
            if result is not None:
                return result

            # Compute
            import streamlit as st
            if show_spinner:
                with st.spinner(f"Computing {func.__name__}..."):
                    result = func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            cache.set(cache_key, result, ttl)
            return result

        return wrapper
    return decorator
