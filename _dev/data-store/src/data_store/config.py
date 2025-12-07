"""
Configuration management for data-store module.
"""

import os
from typing import Dict, Any, Optional


class StoreConfig:
    """Configuration for data store."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize configuration.
        
        Args:
            config: Configuration dictionary or None to load from environment
        """
        if config is None:
            config = self._load_from_env()
        
        self.backend = config.get("backend", "sqlite")
        self.config = config.get("config", {})
    
    def _load_from_env(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        backend = os.getenv("DATA_STORE_BACKEND", "sqlite")
        config = {}
        
        if backend == "mongodb":
            config = {
                "connection_string": os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
                "database": os.getenv("MONGODB_DATABASE", "trainer_data"),
                "collection": os.getenv("MONGODB_COLLECTION", "data_store"),
            }
        elif backend == "postgresql":
            config = {
                "host": os.getenv("POSTGRES_HOST", "localhost"),
                "port": int(os.getenv("POSTGRES_PORT", "5432")),
                "database": os.getenv("POSTGRES_DATABASE", "trainer_data"),
                "user": os.getenv("POSTGRES_USER", "postgres"),
                "password": os.getenv("POSTGRES_PASSWORD", ""),
            }
        elif backend == "redis":
            config = {
                "host": os.getenv("REDIS_HOST", "localhost"),
                "port": int(os.getenv("REDIS_PORT", "6379")),
                "db": int(os.getenv("REDIS_DB", "0")),
                "password": os.getenv("REDIS_PASSWORD"),
            }
        else:  # sqlite
            config = {
                "database_path": os.getenv("SQLITE_DATABASE_PATH", "data/trainer.db"),
            }
        
        return {
            "backend": backend,
            "config": config
        }

