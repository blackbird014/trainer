"""
Abstract base class for data store implementations.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from data_store.models import StoredData, QueryResult, LoadResult


class DataStore(ABC):
    """Abstract base class for data store implementations."""
    
    def __init__(self, **kwargs):
        """Initialize the data store."""
        self.config = kwargs
    
    @abstractmethod
    def store(self, key: str, data: Any, metadata: Optional[Dict[str, Any]] = None, 
              ttl: Optional[int] = None) -> str:
        """
        Store data with the given key.
        
        Args:
            key: Unique key for the data
            data: Data to store
            metadata: Optional metadata dictionary
            ttl: Optional time-to-live in seconds
            
        Returns:
            The storage key
        """
        pass
    
    @abstractmethod
    def retrieve(self, key: str) -> Optional[StoredData]:
        """
        Retrieve data by key.
        
        Args:
            key: The storage key
            
        Returns:
            StoredData if found, None otherwise
        """
        pass
    
    @abstractmethod
    def query(self, filters: Dict[str, Any], limit: Optional[int] = None,
              sort: Optional[Dict[str, int]] = None, offset: int = 0) -> QueryResult:
        """
        Query data by filters.
        
        Args:
            filters: Dictionary of filter criteria
            limit: Maximum number of results
            sort: Sort specification (field -> 1 for asc, -1 for desc)
            offset: Number of results to skip
            
        Returns:
            QueryResult with matching items
        """
        pass
    
    @abstractmethod
    def update(self, key: str, data: Any, metadata: Optional[Dict] = None) -> bool:
        """
        Update existing data.
        
        Args:
            key: The storage key
            data: New data
            metadata: Optional metadata to merge
            
        Returns:
            True if updated, False if not found
        """
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """
        Delete data by key.
        
        Args:
            key: The storage key
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        Check if a key exists.
        
        Args:
            key: The storage key
            
        Returns:
            True if exists, False otherwise
        """
        pass
    
    @abstractmethod
    def get_freshness(self, key: str) -> Optional[datetime]:
        """
        Get the last update time for a key.
        
        Args:
            key: The storage key
            
        Returns:
            datetime of last update, or None if not found
        """
        pass
    
    def aggregate(self, pipeline: List[Dict]) -> List[Dict]:
        """
        Run an aggregation pipeline (MongoDB-style).
        
        Args:
            pipeline: List of aggregation stages
            
        Returns:
            List of aggregated results
        """
        # Default implementation: not all stores support aggregation
        raise NotImplementedError("Aggregation not supported by this store")
    
    def count(self, filters: Dict[str, Any]) -> int:
        """
        Count items matching filters.
        
        Args:
            filters: Filter criteria
            
        Returns:
            Number of matching items
        """
        result = self.query(filters)
        return result.total
    
    def distinct(self, field: str, filters: Optional[Dict] = None) -> List[Any]:
        """
        Get distinct values for a field.
        
        Args:
            field: Field name
            filters: Optional filter criteria
            
        Returns:
            List of distinct values
        """
        # Default implementation: query and extract distinct values
        filters = filters or {}
        result = self.query(filters, limit=10000)  # Large limit for distinct
        
        distinct_values = set()
        for item in result.items:
            if isinstance(item.data, dict) and field in item.data:
                distinct_values.add(item.data[field])
            elif isinstance(item.metadata, dict) and field in item.metadata:
                distinct_values.add(item.metadata[field])
        
        return list(distinct_values)
    
    def bulk_store(self, items: List[Dict[str, Any]]) -> LoadResult:
        """
        Store multiple items at once.
        
        Args:
            items: List of dictionaries with 'key', 'data', and optional 'metadata'
            
        Returns:
            LoadResult with operation status
        """
        keys = []
        errors = []
        
        for item in items:
            try:
                key = self.store(
                    key=item["key"],
                    data=item["data"],
                    metadata=item.get("metadata"),
                    ttl=item.get("ttl")
                )
                keys.append(key)
            except Exception as e:
                errors.append(f"Error storing {item.get('key', 'unknown')}: {str(e)}")
        
        return LoadResult(
            success=len(errors) == 0,
            records_loaded=len(keys),
            errors=errors,
            keys=keys
        )

