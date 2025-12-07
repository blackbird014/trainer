"""
Tests for data models.
"""

import pytest
from datetime import datetime
from data_store.models import StoredData, QueryResult, LoadResult


def test_stored_data():
    """Test StoredData model."""
    data = StoredData(
        key="test_key",
        data={"value": 42},
        source="test_source",
        stored_at=datetime.now(),
        updated_at=datetime.now(),
        metadata={"extra": "info"},
        version=1,
        ttl=3600
    )
    
    assert data.key == "test_key"
    assert data.data == {"value": 42}
    assert data.source == "test_source"
    assert data.version == 1
    assert data.ttl == 3600


def test_query_result():
    """Test QueryResult model."""
    items = [
        StoredData(key="key1", data={"value": 1}, source="test"),
        StoredData(key="key2", data={"value": 2}, source="test"),
    ]
    
    result = QueryResult(
        items=items,
        total=2,
        limit=10,
        offset=0
    )
    
    assert len(result.items) == 2
    assert result.total == 2
    assert result.limit == 10


def test_load_result():
    """Test LoadResult model."""
    result = LoadResult(
        success=True,
        records_loaded=5,
        errors=[],
        keys=["key1", "key2", "key3"]
    )
    
    assert result.success is True
    assert result.records_loaded == 5
    assert len(result.keys) == 3

