"""
Tests for base DataStore class.
"""

import pytest
from typing import Any
from datetime import datetime
from data_store.base import DataStore
from data_store.models import StoredData, QueryResult


class MockStore(DataStore):
    """Mock store for testing base class."""
    
    def __init__(self):
        self._data = {}
        super().__init__()
    
    def store(self, key: str, data: Any, metadata=None, ttl=None):
        self._data[key] = {
            "data": data,
            "metadata": metadata or {},
            "ttl": ttl,
            "stored_at": datetime.now(),
            "updated_at": datetime.now(),
            "version": 1
        }
        return key
    
    def retrieve(self, key: str):
        if key not in self._data:
            return None
        item = self._data[key]
        return StoredData(
            key=key,
            data=item["data"],
            source=item["metadata"].get("source", "unknown"),
            stored_at=item["stored_at"],
            updated_at=item["updated_at"],
            metadata=item["metadata"],
            version=item["version"],
            ttl=item["ttl"]
        )
    
    def query(self, filters, limit=None, sort=None, offset=0):
        items = []
        for key, item in self._data.items():
            stored = self.retrieve(key)
            if stored:
                items.append(stored)
        
        return QueryResult(items=items, total=len(items), limit=limit, offset=offset)
    
    def update(self, key: str, data: Any, metadata=None):
        if key not in self._data:
            return False
        self._data[key]["data"] = data
        if metadata:
            self._data[key]["metadata"].update(metadata)
        self._data[key]["updated_at"] = datetime.now()
        self._data[key]["version"] += 1
        return True
    
    def delete(self, key: str):
        if key not in self._data:
            return False
        del self._data[key]
        return True
    
    def exists(self, key: str):
        return key in self._data
    
    def get_freshness(self, key: str):
        if key not in self._data:
            return None
        return self._data[key]["updated_at"]


def test_store_and_retrieve():
    """Test storing and retrieving data."""
    store = MockStore()
    
    key = store.store("test_key", {"value": 42}, metadata={"source": "test"})
    assert key == "test_key"
    
    stored = store.retrieve("test_key")
    assert stored is not None
    assert stored.key == "test_key"
    assert stored.data == {"value": 42}
    assert stored.metadata["source"] == "test"


def test_update():
    """Test updating data."""
    store = MockStore()
    
    store.store("test_key", {"value": 42})
    success = store.update("test_key", {"value": 100})
    
    assert success is True
    stored = store.retrieve("test_key")
    assert stored.data == {"value": 100}


def test_delete():
    """Test deleting data."""
    store = MockStore()
    
    store.store("test_key", {"value": 42})
    assert store.exists("test_key") is True
    
    success = store.delete("test_key")
    assert success is True
    assert store.exists("test_key") is False


def test_bulk_store():
    """Test bulk storage."""
    store = MockStore()
    
    items = [
        {"key": "key1", "data": {"value": 1}},
        {"key": "key2", "data": {"value": 2}},
    ]
    
    result = store.bulk_store(items)
    assert result.success is True
    assert result.records_loaded == 2
    assert len(result.keys) == 2


def test_count():
    """Test counting items."""
    store = MockStore()
    
    store.store("key1", {"value": 1}, metadata={"source": "test"})
    store.store("key2", {"value": 2}, metadata={"source": "test"})
    
    count = store.count({"source": "test"})
    assert count == 2


def test_distinct():
    """Test distinct values."""
    store = MockStore()
    
    store.store("key1", {"category": "A"}, metadata={"source": "test"})
    store.store("key2", {"category": "B"}, metadata={"source": "test"})
    store.store("key3", {"category": "A"}, metadata={"source": "test"})
    
    distinct = store.distinct("category", {"source": "test"})
    assert len(distinct) == 2
    assert "A" in distinct
    assert "B" in distinct

