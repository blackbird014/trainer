"""
MongoDB storage backend implementation.

Recommended for production deployments with diverse data types.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

try:
    from pymongo import MongoClient
    from pymongo.collection import Collection
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False
    MongoClient = None
    Collection = None

from data_store.base import DataStore
from data_store.models import StoredData, QueryResult


class MongoDBStore(DataStore):
    """MongoDB-based data store implementation."""
    
    def __init__(self, connection_string: str = "mongodb://localhost:27017",
                 database: str = "trainer_data", collection: str = "data_store", **kwargs):
        """
        Initialize MongoDB store.
        
        Args:
            connection_string: MongoDB connection string
            database: Database name
            collection: Collection name
        """
        super().__init__(**kwargs)
        
        if not MONGO_AVAILABLE:
            raise ImportError(
                "pymongo is required for MongoDBStore. "
                "Install with: pip install trainer-data-store[mongodb]"
            )
        
        self.client = MongoClient(connection_string)
        self.db = self.client[database]
        self.collection: Collection = self.db[collection]
        
        # Create indexes
        self.collection.create_index("key", unique=True)
        self.collection.create_index("source")
        self.collection.create_index("stored_at")
        self.collection.create_index("expires_at", expireAfterSeconds=0)
    
    def store(self, key: str, data: Any, metadata: Optional[Dict[str, Any]] = None,
              ttl: Optional[int] = None) -> str:
        """Store data."""
        now = datetime.now()
        expires_at = None
        if ttl:
            expires_at = now + timedelta(seconds=ttl)
        
        # Get current version
        existing = self.collection.find_one({"key": key})
        version = (existing.get("version", 0) + 1) if existing else 1
        
        doc = {
            "key": key,
            "data": data,
            "source": metadata.get("source", "unknown") if metadata else "unknown",
            "stored_at": now,
            "updated_at": now,
            "metadata": metadata or {},
            "version": version,
            "ttl": ttl,
            "expires_at": expires_at
        }
        
        self.collection.replace_one({"key": key}, doc, upsert=True)
        return key
    
    def retrieve(self, key: str) -> Optional[StoredData]:
        """Retrieve data by key."""
        doc = self.collection.find_one({"key": key})
        
        if not doc:
            return None
        
        # Check expiry
        if doc.get("expires_at") and datetime.now() > doc["expires_at"]:
            self.delete(key)
            return None
        
        return StoredData(
            key=doc["key"],
            data=doc["data"],
            source=doc["source"],
            stored_at=doc["stored_at"],
            updated_at=doc["updated_at"],
            metadata=doc.get("metadata", {}),
            version=doc.get("version", 1),
            ttl=doc.get("ttl")
        )
    
    def query(self, filters: Dict[str, Any], limit: Optional[int] = None,
              sort: Optional[Dict[str, int]] = None, offset: int = 0) -> QueryResult:
        """Query data by filters."""
        # Build MongoDB query
        query = {}
        
        # Expiry filter
        expiry_or = [
            {"expires_at": {"$exists": False}},
            {"expires_at": None},
            {"expires_at": {"$gt": datetime.now()}}
        ]
        
        # Build field filters
        field_filters = []
        for field, value in filters.items():
            if field == "source":
                query["source"] = value
            elif field == "key":
                query["key"] = value
            else:
                # Search in metadata or data
                field_filters.append({f"metadata.{field}": value})
                field_filters.append({f"data.{field}": value})
        
        # Combine expiry and field filters with $and
        if field_filters:
            query["$and"] = [
                {"$or": expiry_or},
                {"$or": field_filters}
            ]
        else:
            query["$or"] = expiry_or
        
        # Count total
        total = self.collection.count_documents(query)
        
        # Build sort
        sort_spec = [("updated_at", -1)]  # Default sort
        if sort:
            sort_spec = [(field, direction) for field, direction in sort.items()]
        
        # Query
        cursor = self.collection.find(query).sort(sort_spec).skip(offset)
        if limit:
            cursor = cursor.limit(limit)
        
        items = []
        for doc in cursor:
            items.append(StoredData(
                key=doc["key"],
                data=doc["data"],
                source=doc["source"],
                stored_at=doc["stored_at"],
                updated_at=doc["updated_at"],
                metadata=doc.get("metadata", {}),
                version=doc.get("version", 1),
                ttl=doc.get("ttl")
            ))
        
        return QueryResult(
            items=items,
            total=total,
            limit=limit,
            offset=offset
        )
    
    def update(self, key: str, data: Any, metadata: Optional[Dict] = None) -> bool:
        """Update existing data."""
        existing = self.collection.find_one({"key": key})
        if not existing:
            return False
        
        # Merge metadata
        merged_metadata = existing.get("metadata", {}).copy()
        if metadata:
            merged_metadata.update(metadata)
        
        self.collection.update_one(
            {"key": key},
            {
                "$set": {
                    "data": data,
                    "metadata": merged_metadata,
                    "updated_at": datetime.now()
                }
            }
        )
        return True
    
    def delete(self, key: str) -> bool:
        """Delete data by key."""
        result = self.collection.delete_one({"key": key})
        return result.deleted_count > 0
    
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        return self.collection.count_documents({"key": key}) > 0
    
    def get_freshness(self, key: str) -> Optional[datetime]:
        """Get last update time."""
        doc = self.collection.find_one({"key": key}, {"updated_at": 1})
        return doc.get("updated_at") if doc else None
    
    def aggregate(self, pipeline: List[Dict]) -> List[Dict]:
        """Run aggregation pipeline."""
        return list(self.collection.aggregate(pipeline))

