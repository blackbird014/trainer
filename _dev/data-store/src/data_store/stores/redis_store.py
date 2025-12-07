"""
Redis storage backend implementation.

Recommended for caching and high-performance scenarios.
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

from data_store.base import DataStore
from data_store.models import StoredData, QueryResult


class RedisStore(DataStore):
    """Redis-based data store implementation."""
    
    def __init__(self, host: str = "localhost", port: int = 6379,
                 db: int = 0, password: Optional[str] = None,
                 key_prefix: str = "data_store:", **kwargs):
        """
        Initialize Redis store.
        
        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password
            key_prefix: Prefix for all keys
        """
        super().__init__(**kwargs)
        
        if not REDIS_AVAILABLE:
            raise ImportError(
                "redis is required for RedisStore. "
                "Install with: pip install trainer-data-store[redis]"
            )
        
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=False  # We'll handle encoding ourselves
        )
        self.key_prefix = key_prefix
    
    def _make_key(self, key: str) -> bytes:
        """Create full key with prefix."""
        return f"{self.key_prefix}{key}".encode('utf-8')
    
    def _serialize(self, obj: Any) -> bytes:
        """Serialize object to JSON bytes."""
        return json.dumps(obj, default=str).encode('utf-8')
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize JSON bytes to object."""
        return json.loads(data.decode('utf-8'))
    
    def store(self, key: str, data: Any, metadata: Optional[Dict[str, Any]] = None,
              ttl: Optional[int] = None) -> str:
        """Store data."""
        now = datetime.now()
        
        # Get current version
        existing_key = self._make_key(key)
        existing_data = self.client.get(existing_key)
        version = 1
        if existing_data:
            existing = self._deserialize(existing_data)
            version = existing.get("version", 0) + 1
        
        doc = {
            "key": key,
            "data": data,
            "source": metadata.get("source", "unknown") if metadata else "unknown",
            "stored_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "metadata": metadata or {},
            "version": version,
            "ttl": ttl
        }
        
        redis_key = self._make_key(key)
        self.client.set(redis_key, self._serialize(doc), ex=ttl)
        
        # Also store in index for querying
        source = doc["source"]
        index_key = f"{self.key_prefix}index:source:{source}".encode('utf-8')
        self.client.sadd(index_key, key.encode('utf-8'))
        if ttl:
            self.client.expire(index_key, ttl)
        
        return key
    
    def retrieve(self, key: str) -> Optional[StoredData]:
        """Retrieve data by key."""
        redis_key = self._make_key(key)
        data = self.client.get(redis_key)
        
        if not data:
            return None
        
        doc = self._deserialize(data)
        
        return StoredData(
            key=doc["key"],
            data=doc["data"],
            source=doc["source"],
            stored_at=datetime.fromisoformat(doc["stored_at"]),
            updated_at=datetime.fromisoformat(doc["updated_at"]),
            metadata=doc.get("metadata", {}),
            version=doc.get("version", 1),
            ttl=doc.get("ttl")
        )
    
    def query(self, filters: Dict[str, Any], limit: Optional[int] = None,
              sort: Optional[Dict[str, int]] = None, offset: int = 0) -> QueryResult:
        """Query data by filters."""
        # Redis doesn't support complex queries efficiently
        # We'll use simple source-based filtering
        
        items = []
        
        if "source" in filters:
            # Use index
            source = filters["source"]
            index_key = f"{self.key_prefix}index:source:{source}".encode('utf-8')
            keys = self.client.smembers(index_key)
            
            for key_bytes in keys:
                key = key_bytes.decode('utf-8')
                stored = self.retrieve(key)
                if stored:
                    # Apply other filters
                    matches = True
                    for field, value in filters.items():
                        if field == "source":
                            continue
                        if field == "key" and key != value:
                            matches = False
                            break
                        if isinstance(stored.data, dict) and stored.data.get(field) != value:
                            matches = False
                            break
                        if isinstance(stored.metadata, dict) and stored.metadata.get(field) != value:
                            matches = False
                            break
                    
                    if matches:
                        items.append(stored)
        elif "key" in filters:
            # Direct key lookup
            stored = self.retrieve(filters["key"])
            if stored:
                items.append(stored)
        else:
            # Scan all keys (inefficient, but works)
            pattern = f"{self.key_prefix}*"
            for key_bytes in self.client.scan_iter(match=pattern):
                if key_bytes.startswith(f"{self.key_prefix}index:".encode('utf-8')):
                    continue
                
                key = key_bytes.decode('utf-8').replace(self.key_prefix, "")
                stored = self.retrieve(key)
                if stored:
                    items.append(stored)
        
        # Sort
        if sort:
            field = list(sort.keys())[0]
            reverse = sort[field] == -1
            
            def sort_key(item: StoredData):
                if field == "updated_at":
                    return item.updated_at
                elif field == "stored_at":
                    return item.stored_at
                elif field == "source":
                    return item.source
                elif field == "key":
                    return item.key
                return None
            
            items.sort(key=sort_key, reverse=reverse)
        else:
            items.sort(key=lambda x: x.updated_at, reverse=True)
        
        # Apply offset and limit
        total = len(items)
        items = items[offset:]
        if limit:
            items = items[:limit]
        
        return QueryResult(
            items=items,
            total=total,
            limit=limit,
            offset=offset
        )
    
    def update(self, key: str, data: Any, metadata: Optional[Dict] = None) -> bool:
        """Update existing data."""
        stored = self.retrieve(key)
        if not stored:
            return False
        
        # Merge metadata
        merged_metadata = stored.metadata.copy()
        if metadata:
            merged_metadata.update(metadata)
        
        self.store(key, data, merged_metadata, stored.ttl)
        return True
    
    def delete(self, key: str) -> bool:
        """Delete data by key."""
        redis_key = self._make_key(key)
        
        # Get source for index cleanup
        stored = self.retrieve(key)
        if stored:
            index_key = f"{self.key_prefix}index:source:{stored.source}".encode('utf-8')
            self.client.srem(index_key, key.encode('utf-8'))
        
        deleted = self.client.delete(redis_key) > 0
        return deleted
    
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        redis_key = self._make_key(key)
        return self.client.exists(redis_key) > 0
    
    def get_freshness(self, key: str) -> Optional[datetime]:
        """Get last update time."""
        stored = self.retrieve(key)
        return stored.updated_at if stored else None

