"""Tests for base DataRetriever class."""

import time
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from data_retriever.base import DataRetriever, RetrievalResult
from data_retriever.cache import DataCache
from data_retriever.schema import Schema, Field, FieldType


class MockRetriever(DataRetriever):
    """Mock retriever for testing."""

    def retrieve(self, query):
        return RetrievalResult(
            data={"test": "data"},
            source=self.source_name,
        )

    def get_schema(self):
        return Schema(
            name="test_schema",
            fields=[Field("test", FieldType.STRING)],
        )


def test_retrieval_result():
    """Test RetrievalResult dataclass."""
    result = RetrievalResult(
        data={"key": "value"},
        source="test",
    )

    assert result.data == {"key": "value"}
    assert result.source == "test"
    assert result.success is True
    assert result.error is None
    assert isinstance(result.retrieved_at, datetime)


def test_retrieval_result_to_dict():
    """Test RetrievalResult.to_dict()."""
    result = RetrievalResult(
        data={"key": "value"},
        source="test",
    )

    result_dict = result.to_dict()
    assert result_dict["data"] == {"key": "value"}
    assert result_dict["source"] == "test"
    assert result_dict["success"] is True
    assert "retrieved_at" in result_dict


def test_data_retriever_init():
    """Test DataRetriever initialization."""
    retriever = MockRetriever(source_name="test")
    assert retriever.source_name == "test"
    assert retriever.cache is None
    assert retriever.rate_limit is None


def test_data_retriever_with_cache():
    """Test DataRetriever with cache."""
    cache = DataCache()
    retriever = MockRetriever(source_name="test", cache=cache)

    query = {"test": "query"}
    result1 = retriever.retrieve_with_cache(query)
    result2 = retriever.retrieve_with_cache(query)

    # Second call should use cache
    assert result1.data == result2.data


def test_data_retriever_rate_limit():
    """Test DataRetriever rate limiting."""
    retriever = MockRetriever(source_name="test", rate_limit=10.0)  # 10 req/sec

    start = time.time()
    retriever._apply_rate_limit()
    retriever._apply_rate_limit()
    elapsed = time.time() - start

    # Should have waited at least 0.1 seconds (1/10)
    assert elapsed >= 0.09  # Allow small margin


def test_cache_key_generation():
    """Test cache key generation."""
    retriever = MockRetriever(source_name="test")
    query = {"ticker": "AAPL", "year": 2023}

    key1 = retriever._get_cache_key(query)
    key2 = retriever._get_cache_key(query)

    assert key1 == key2
    assert key1.startswith("test:")


def test_retrieve_with_cache_stores_result():
    """Test that retrieve_with_cache stores successful results."""
    cache = DataCache()
    retriever = MockRetriever(source_name="test", cache=cache)

    query = {"test": "query"}
    result = retriever.retrieve_with_cache(query)

    assert result.success
    assert cache.size() == 1


def test_retrieve_with_cache_skips_failed():
    """Test that failed retrievals are not cached."""
    cache = DataCache()

    class FailingRetriever(MockRetriever):
        def retrieve(self, query):
            return RetrievalResult(
                data={},
                source=self.source_name,
                success=False,
                error="Test error",
            )

    retriever = FailingRetriever(source_name="test", cache=cache)
    query = {"test": "query"}
    result = retriever.retrieve_with_cache(query)

    assert not result.success
    assert cache.size() == 0  # Failed results not cached

