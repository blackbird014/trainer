"""
Data models for data-store module.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class StoredData(BaseModel):
    """Model representing stored data."""
    
    model_config = ConfigDict(
        # Pydantic v2 handles datetime serialization automatically
    )
    
    key: str = Field(..., description="Unique key for the stored data")
    data: Any = Field(..., description="The actual data being stored")
    source: str = Field(..., description="Source of the data (e.g., 'yahoo_finance')")
    stored_at: datetime = Field(default_factory=datetime.now, description="When data was stored")
    updated_at: datetime = Field(default_factory=datetime.now, description="When data was last updated")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    version: int = Field(default=1, description="Version number of the data")
    ttl: Optional[int] = Field(default=None, description="Time-to-live in seconds")


class QueryResult(BaseModel):
    """Result of a query operation."""
    
    items: list[StoredData] = Field(default_factory=list, description="Matching items")
    total: int = Field(default=0, description="Total number of matching items")
    limit: Optional[int] = Field(default=None, description="Query limit")
    offset: int = Field(default=0, description="Query offset")


class LoadResult(BaseModel):
    """Result of a load operation."""
    
    success: bool = Field(..., description="Whether the operation succeeded")
    records_loaded: int = Field(default=0, description="Number of records loaded")
    errors: list[str] = Field(default_factory=list, description="Any errors encountered")
    keys: list[str] = Field(default_factory=list, description="Keys of stored items")

