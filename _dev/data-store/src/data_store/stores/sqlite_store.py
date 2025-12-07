"""
SQLite storage backend implementation.

Perfect for development and small-scale deployments.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from data_store.base import DataStore
from data_store.models import StoredData, QueryResult


class SQLiteStore(DataStore):
    """SQLite-based data store implementation."""
    
    def __init__(self, database_path: str = "data/trainer.db", **kwargs):
        """
        Initialize SQLite store.
        
        Args:
            database_path: Path to SQLite database file
        """
        super().__init__(**kwargs)
        self.database_path = database_path
        
        # Create directory if needed
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_store (
                key TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                source TEXT NOT NULL,
                stored_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                metadata TEXT NOT NULL,
                version INTEGER NOT NULL DEFAULT 1,
                ttl INTEGER,
                expires_at TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_source ON data_store(source)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_stored_at ON data_store(stored_at)
        """)
        
        conn.commit()
        conn.close()
    
    def _get_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.database_path)
    
    def _serialize_data(self, data: Any) -> str:
        """Serialize data to JSON string."""
        return json.dumps(data, default=str)
    
    def _deserialize_data(self, data_str: str) -> Any:
        """Deserialize JSON string to data."""
        return json.loads(data_str)
    
    def _check_expiry(self, expires_at: Optional[str]) -> bool:
        """Check if data has expired."""
        if expires_at is None:
            return False
        expires = datetime.fromisoformat(expires_at)
        return datetime.now() > expires
    
    def store(self, key: str, data: Any, metadata: Optional[Dict[str, Any]] = None,
              ttl: Optional[int] = None) -> str:
        """Store data."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        expires_at = None
        if ttl:
            expires = datetime.now().timestamp() + ttl
            expires_at = datetime.fromtimestamp(expires).isoformat()
        
        # Check if exists to increment version
        cursor.execute("SELECT version FROM data_store WHERE key = ?", (key,))
        row = cursor.fetchone()
        version = (row[0] + 1) if row else 1
        
        cursor.execute("""
            INSERT OR REPLACE INTO data_store 
            (key, data, source, stored_at, updated_at, metadata, version, ttl, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            key,
            self._serialize_data(data),
            metadata.get("source", "unknown") if metadata else "unknown",
            now,
            now,
            self._serialize_data(metadata or {}),
            version,
            ttl,
            expires_at
        ))
        
        conn.commit()
        conn.close()
        return key
    
    def retrieve(self, key: str) -> Optional[StoredData]:
        """Retrieve data by key."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT key, data, source, stored_at, updated_at, metadata, version, ttl, expires_at
            FROM data_store WHERE key = ?
        """, (key,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        key_val, data_str, source, stored_at, updated_at, metadata_str, version, ttl, expires_at = row
        
        # Check expiry
        if self._check_expiry(expires_at):
            self.delete(key)
            return None
        
        return StoredData(
            key=key_val,
            data=self._deserialize_data(data_str),
            source=source,
            stored_at=datetime.fromisoformat(stored_at),
            updated_at=datetime.fromisoformat(updated_at),
            metadata=self._deserialize_data(metadata_str),
            version=version,
            ttl=ttl
        )
    
    def query(self, filters: Dict[str, Any], limit: Optional[int] = None,
              sort: Optional[Dict[str, int]] = None, offset: int = 0) -> QueryResult:
        """Query data by filters."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Build WHERE clause
        conditions = ["(expires_at IS NULL OR expires_at > ?)"]
        params = [datetime.now().isoformat()]
        
        for field, value in filters.items():
            if field == "source":
                conditions.append("source = ?")
                params.append(value)
            elif field == "key":
                conditions.append("key = ?")
                params.append(value)
            else:
                # For other fields, search in metadata JSON
                # Use JSON_EXTRACT for better matching (SQLite 3.9+)
                # Fallback to LIKE for older SQLite versions
                conditions.append("(metadata LIKE ? OR json_extract(metadata, '$.' || ?) = ?)")
                params.extend([f'%"{field}":"{value}"%', field, json.dumps(value)])
        
        where_clause = " AND ".join(conditions)
        
        # Build ORDER BY
        order_by = "updated_at DESC"
        if sort:
            field = list(sort.keys())[0]
            direction = "DESC" if sort[field] == -1 else "ASC"
            if field in ["stored_at", "updated_at", "source", "key"]:
                order_by = f"{field} {direction}"
        
        # Count total (with same filters)
        count_query = f"SELECT COUNT(*) FROM data_store WHERE {where_clause}"
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # Query with limit and offset
        query = f"""
            SELECT key, data, source, stored_at, updated_at, metadata, version, ttl, expires_at
            FROM data_store WHERE {where_clause}
            ORDER BY {order_by}
        """
        
        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        items = []
        for row in rows:
            key_val, data_str, source, stored_at, updated_at, metadata_str, version, ttl, expires_at = row
            
            if not self._check_expiry(expires_at):
                stored_data = StoredData(
                    key=key_val,
                    data=self._deserialize_data(data_str),
                    source=source,
                    stored_at=datetime.fromisoformat(stored_at),
                    updated_at=datetime.fromisoformat(updated_at),
                    metadata=self._deserialize_data(metadata_str),
                    version=version,
                    ttl=ttl
                )
                
                # Apply additional filters that weren't handled in SQL (for metadata fields)
                matches = True
                for field, value in filters.items():
                    if field in ["source", "key"]:
                        continue  # Already filtered in SQL
                    # Check metadata
                    if isinstance(stored_data.metadata, dict) and stored_data.metadata.get(field) != value:
                        matches = False
                        break
                
                if matches:
                    items.append(stored_data)
        
        # Update total to match filtered items count
        total = len(items)
        
        conn.close()
        
        return QueryResult(
            items=items,
            total=total,
            limit=limit,
            offset=offset
        )
    
    def update(self, key: str, data: Any, metadata: Optional[Dict] = None) -> bool:
        """Update existing data."""
        if not self.exists(key):
            return False
        
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
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM data_store WHERE key = ?", (key,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        return deleted
    
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM data_store WHERE key = ?", (key,))
        exists = cursor.fetchone() is not None
        
        conn.close()
        return exists
    
    def get_freshness(self, key: str) -> Optional[datetime]:
        """Get last update time."""
        stored = self.retrieve(key)
        return stored.updated_at if stored else None

