"""
Data Store Module - Centralized data persistence layer.

Provides unified interface for storing and retrieving data across multiple
storage backends (MongoDB, PostgreSQL, SQLite, Redis).
"""

from data_store.base import DataStore
from data_store.models import StoredData
from data_store.registry import StoreRegistry, create_store

__all__ = [
    "DataStore",
    "StoredData",
    "StoreRegistry",
    "create_store",
]

__version__ = "0.1.0"

