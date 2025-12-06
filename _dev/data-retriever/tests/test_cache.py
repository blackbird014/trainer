"""Tests for DataCache."""

import time

import pytest

from data_retriever.cache import DataCache


def test_cache_set_get():
    """Test basic cache set/get operations."""
    cache = DataCache()
    cache.set("key1", {"data": "value1"})

    result = cache.get("key1")
    assert result == {"data": "value1"}


def test_cache_expiration():
    """Test cache expiration."""
    cache = DataCache(default_ttl=1)  # 1 second TTL
    cache.set("key1", {"data": "value1"})

    # Should be available immediately
    assert cache.get("key1") == {"data": "value1"}

    # Wait for expiration
    time.sleep(1.1)

    # Should be expired
    assert cache.get("key1") is None


def test_cache_custom_ttl():
    """Test cache with custom TTL."""
    cache = DataCache(default_ttl=10)
    cache.set("key1", {"data": "value1"}, ttl=1)  # Custom 1 second TTL

    assert cache.get("key1") == {"data": "value1"}

    time.sleep(1.1)
    assert cache.get("key1") is None


def test_cache_max_size():
    """Test cache max size eviction."""
    cache = DataCache(max_size=2)

    cache.set("key1", {"data": "value1"})
    cache.set("key2", {"data": "value2"})
    cache.set("key3", {"data": "value3"})  # Should evict oldest

    # key1 should be evicted (oldest)
    assert cache.get("key1") is None
    assert cache.get("key2") == {"data": "value2"}
    assert cache.get("key3") == {"data": "value3"}


def test_cache_clear():
    """Test cache clearing."""
    cache = DataCache()
    cache.set("key1", {"data": "value1"})
    cache.set("key2", {"data": "value2"})

    assert cache.size() == 2

    cache.clear()
    assert cache.size() == 0
    assert cache.get("key1") is None


def test_cache_remove():
    """Test cache item removal."""
    cache = DataCache()
    cache.set("key1", {"data": "value1"})
    cache.set("key2", {"data": "value2"})

    cache.remove("key1")

    assert cache.get("key1") is None
    assert cache.get("key2") == {"data": "value2"}


def test_cache_size():
    """Test cache size tracking."""
    cache = DataCache()
    assert cache.size() == 0

    cache.set("key1", {"data": "value1"})
    assert cache.size() == 1

    cache.set("key2", {"data": "value2"})
    assert cache.size() == 2

