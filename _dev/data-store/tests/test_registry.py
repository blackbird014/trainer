"""
Tests for store registry and factory.
"""

import pytest
from data_store.registry import StoreRegistry, create_store
from data_store.stores import SQLiteStore, MongoDBStore, PostgreSQLStore, RedisStore


def test_registry_list_stores():
    """Test listing available stores."""
    stores = StoreRegistry.list_stores()
    assert "sqlite" in stores
    assert "mongodb" in stores
    assert "postgresql" in stores
    assert "redis" in stores


def test_registry_get():
    """Test getting store class."""
    store_class = StoreRegistry.get("sqlite")
    assert store_class == SQLiteStore
    
    store_class = StoreRegistry.get("mongodb")
    assert store_class == MongoDBStore


def test_registry_get_invalid():
    """Test getting invalid store type."""
    store_class = StoreRegistry.get("invalid")
    assert store_class is None


def test_create_store_sqlite():
    """Test creating SQLite store."""
    store = create_store("sqlite", database_path=":memory:")
    assert isinstance(store, SQLiteStore)


def test_create_store_invalid():
    """Test creating store with invalid type."""
    with pytest.raises(ValueError, match="Unknown store type"):
        create_store("invalid_type")


def test_registry_register():
    """Test registering custom store."""
    class CustomStore:
        pass
    
    StoreRegistry.register("custom", CustomStore)
    assert StoreRegistry.get("custom") == CustomStore

