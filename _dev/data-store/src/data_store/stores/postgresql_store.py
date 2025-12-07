"""
PostgreSQL storage backend implementation.

Recommended for structured data with ACID requirements.
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    psycopg2 = None
    RealDictCursor = None

from data_store.base import DataStore
from data_store.models import StoredData, QueryResult


class PostgreSQLStore(DataStore):
    """PostgreSQL-based data store implementation."""
    
    def __init__(self, connection_string: str = None, host: str = "localhost",
                 port: int = 5432, database: str = "trainer_data",
                 user: str = "postgres", password: str = "", **kwargs):
        """
        Initialize PostgreSQL store.
        
        Args:
            connection_string: Full connection string (overrides other params)
            host: Database host
            port: Database port
            database: Database name
            user: Database user
            password: Database password
        """
        super().__init__(**kwargs)
        
        if not POSTGRES_AVAILABLE:
            raise ImportError(
                "psycopg2-binary is required for PostgreSQLStore. "
                "Install with: pip install trainer-data-store[postgresql]"
            )
        
        if connection_string:
            self.conn_string = connection_string
        else:
            self.conn_string = f"host={host} port={port} dbname={database} user={user} password={password}"
        
        # Initialize schema
        self._init_schema()
    
    def _get_connection(self):
        """Get database connection."""
        return psycopg2.connect(self.conn_string)
    
    def _init_schema(self):
        """Initialize database schema."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_store (
                key VARCHAR(255) PRIMARY KEY,
                data JSONB NOT NULL,
                source VARCHAR(255) NOT NULL,
                stored_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                metadata JSONB NOT NULL DEFAULT '{}',
                version INTEGER NOT NULL DEFAULT 1,
                ttl INTEGER,
                expires_at TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_source ON data_store(source)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_stored_at ON data_store(stored_at)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_expires_at ON data_store(expires_at)
        """)
        
        conn.commit()
        conn.close()
    
    def store(self, key: str, data: Any, metadata: Optional[Dict[str, Any]] = None,
              ttl: Optional[int] = None) -> str:
        """Store data."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        now = datetime.now()
        expires_at = None
        if ttl:
            expires_at = now + timedelta(seconds=ttl)
        
        # Get current version
        cursor.execute("SELECT version FROM data_store WHERE key = %s", (key,))
        row = cursor.fetchone()
        version = (row[0] + 1) if row else 1
        
        source = metadata.get("source", "unknown") if metadata else "unknown"
        
        cursor.execute("""
            INSERT INTO data_store 
            (key, data, source, stored_at, updated_at, metadata, version, ttl, expires_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (key) DO UPDATE SET
                data = EXCLUDED.data,
                source = EXCLUDED.source,
                updated_at = EXCLUDED.updated_at,
                metadata = EXCLUDED.metadata,
                version = EXCLUDED.version,
                ttl = EXCLUDED.ttl,
                expires_at = EXCLUDED.expires_at
        """, (
            key,
            json.dumps(data, default=str),
            source,
            now,
            now,
            json.dumps(metadata or {}, default=str),
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
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT key, data, source, stored_at, updated_at, metadata, version, ttl, expires_at
            FROM data_store WHERE key = %s
        """, (key,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        # Check expiry
        if row.get("expires_at") and datetime.now() > row["expires_at"]:
            self.delete(key)
            return None
        
        return StoredData(
            key=row["key"],
            data=json.loads(row["data"]),
            source=row["source"],
            stored_at=row["stored_at"],
            updated_at=row["updated_at"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            version=row["version"],
            ttl=row.get("ttl")
        )
    
    def query(self, filters: Dict[str, Any], limit: Optional[int] = None,
              sort: Optional[Dict[str, int]] = None, offset: int = 0) -> QueryResult:
        """Query data by filters."""
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build WHERE clause
        conditions = ["(expires_at IS NULL OR expires_at > %s)"]
        params = [datetime.now()]
        
        for field, value in filters.items():
            if field == "source":
                conditions.append("source = %s")
                params.append(value)
            elif field == "key":
                conditions.append("key = %s")
                params.append(value)
            else:
                # Search in metadata or data JSONB
                conditions.append("(metadata->>%s = %s OR data->>%s = %s)")
                params.extend([field, str(value), field, str(value)])
        
        where_clause = " AND ".join(conditions)
        
        # Build ORDER BY
        order_by = "updated_at DESC"
        if sort:
            field = list(sort.keys())[0]
            direction = "DESC" if sort[field] == -1 else "ASC"
            if field in ["stored_at", "updated_at", "source", "key"]:
                order_by = f"{field} {direction}"
        
        # Count total
        cursor.execute(f"SELECT COUNT(*) FROM data_store WHERE {where_clause}", params)
        total = cursor.fetchone()["count"]
        
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
            items.append(StoredData(
                key=row["key"],
                data=json.loads(row["data"]),
                source=row["source"],
                stored_at=row["stored_at"],
                updated_at=row["updated_at"],
                metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                version=row["version"],
                ttl=row.get("ttl")
            ))
        
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
        
        cursor.execute("DELETE FROM data_store WHERE key = %s", (key,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        return deleted
    
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM data_store WHERE key = %s", (key,))
        exists = cursor.fetchone() is not None
        
        conn.close()
        return exists
    
    def get_freshness(self, key: str) -> Optional[datetime]:
        """Get last update time."""
        stored = self.retrieve(key)
        return stored.updated_at if stored else None

