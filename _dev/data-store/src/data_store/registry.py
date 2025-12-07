"""
Store registry and factory for creating data stores.
"""

from typing import Dict, Optional, Type
from data_store.base import DataStore
from data_store.stores import SQLiteStore, MongoDBStore, PostgreSQLStore, RedisStore


class StoreRegistry:
    """Registry for data store implementations."""
    
    _stores: Dict[str, Type[DataStore]] = {
        "sqlite": SQLiteStore,
        "mongodb": MongoDBStore,
        "postgresql": PostgreSQLStore,
        "redis": RedisStore,
    }
    
    @classmethod
    def register(cls, name: str, store_class: Type[DataStore]):
        """Register a new store implementation."""
        cls._stores[name] = store_class
    
    @classmethod
    def get(cls, name: str) -> Optional[Type[DataStore]]:
        """Get a store class by name."""
        return cls._stores.get(name.lower())
    
    @classmethod
    def list_stores(cls) -> list[str]:
        """List all registered store types."""
        return list(cls._stores.keys())


def create_store(store_type: str, **kwargs) -> DataStore:
    """
    Factory function to create a data store instance.
    
    Args:
        store_type: Type of store ("sqlite", "mongodb", "postgresql", "redis")
        **kwargs: Store-specific configuration
        
    Returns:
        DataStore instance
        
    Raises:
        ValueError: If store type is not recognized
    """
    store_class = StoreRegistry.get(store_type)
    if not store_class:
        available = ", ".join(StoreRegistry.list_stores())
        raise ValueError(
            f"Unknown store type: {store_type}. "
            f"Available types: {available}"
        )
    
    return store_class(**kwargs)

