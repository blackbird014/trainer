"""
Base abstraction for data retrievers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
import time
import json


@dataclass
class RetrievalResult:
    """Result of a data retrieval operation."""

    data: Dict[str, Any]
    source: str
    retrieved_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "data": self.data,
            "source": self.source,
            "retrieved_at": self.retrieved_at.isoformat(),
            "metadata": self.metadata,
            "success": self.success,
            "error": self.error,
        }


class DataRetriever(ABC):
    """
    Abstract base class for data retrievers.

    All retrievers must implement:
    - retrieve(): Fetch data from the source
    - get_schema(): Return the expected schema for retrieved data
    """

    def __init__(
        self,
        source_name: str,
        cache: Optional["DataCache"] = None,
        rate_limit: Optional[float] = None,
        enable_metrics: bool = True,
    ):
        """
        Initialize data retriever.

        Args:
            source_name: Name of the data source
            cache: Optional cache instance for caching results
            rate_limit: Optional rate limit in requests per second
            enable_metrics: Enable Prometheus metrics collection
        """
        self.source_name = source_name
        self.cache = cache
        self.rate_limit = rate_limit
        self._last_request_time: Optional[float] = None
        self.enable_metrics = enable_metrics
        
        # Initialize metrics collector if enabled
        if enable_metrics:
            try:
                from data_retriever.metrics import MetricsCollector
                self.metrics = MetricsCollector(source_name)
            except ImportError:
                self.metrics = None
                self.enable_metrics = False
        else:
            self.metrics = None

    @abstractmethod
    def retrieve(self, query: Dict[str, Any]) -> RetrievalResult:
        """
        Retrieve data based on query parameters.

        Args:
            query: Query parameters specific to the retriever

        Returns:
            RetrievalResult containing the retrieved data
        """
        pass

    @abstractmethod
    def get_schema(self) -> "Schema":
        """
        Get the schema for data returned by this retriever.

        Returns:
            Schema object describing the data structure
        """
        pass

    def _apply_rate_limit(self):
        """Apply rate limiting if configured."""
        if self.rate_limit is None:
            return

        if self._last_request_time is not None:
            min_interval = 1.0 / self.rate_limit
            elapsed = time.time() - self._last_request_time
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)

        self._last_request_time = time.time()

    def _get_cache_key(self, query: Dict[str, Any]) -> str:
        """Generate cache key from query."""
        query_str = json.dumps(query, sort_keys=True)
        return f"{self.source_name}:{hash(query_str)}"

    def _check_cache(self, query: Dict[str, Any]) -> Optional[RetrievalResult]:
        """Check cache for existing result."""
        if self.cache is None:
            return None

        cache_key = self._get_cache_key(query)
        cached = self.cache.get(cache_key)
        if cached is not None:
            # Convert cached dict back to RetrievalResult
            return RetrievalResult(
                data=cached["data"],
                source=cached["source"],
                retrieved_at=datetime.fromisoformat(cached["retrieved_at"]),
                metadata=cached.get("metadata", {}),
                success=cached.get("success", True),
                error=cached.get("error"),
            )
        return None

    def _store_cache(self, query: Dict[str, Any], result: RetrievalResult):
        """Store result in cache."""
        if self.cache is None:
            return

        cache_key = self._get_cache_key(query)
        self.cache.set(cache_key, result.to_dict())

    def retrieve_with_cache(self, query: Dict[str, Any]) -> RetrievalResult:
        """
        Retrieve data with caching support and metrics tracking.

        Args:
            query: Query parameters specific to the retriever

        Returns:
            RetrievalResult containing the retrieved data
        """
        start_time = time.time()
        
        # Track active operations
        if self.metrics:
            self.metrics.increment_active_operations()
        
        try:
            # Check cache first
            cached = self._check_cache(query)
            if cached is not None:
                if self.metrics:
                    self.metrics.track_cache_hit()
                    self.metrics.track_operation("success")
                    self.metrics.track_duration(time.time() - start_time)
                if self.metrics:
                    self.metrics.decrement_active_operations()
                return cached
            
            if self.metrics:
                self.metrics.track_cache_miss()

            # Apply rate limiting
            self._apply_rate_limit()

            # Retrieve data
            result = self.retrieve(query)
            
            duration = time.time() - start_time

            # Track metrics
            if self.metrics:
                status = "success" if result.success else "error"
                self.metrics.track_operation(status)
                self.metrics.track_duration(duration)
                
                if not result.success:
                    error_type = "retrieval_error"
                    if "not found" in result.error.lower():
                        error_type = "not_found"
                    elif "timeout" in result.error.lower():
                        error_type = "timeout"
                    elif "rate limit" in result.error.lower():
                        error_type = "rate_limit"
                    self.metrics.track_error(error_type)
                else:
                    # Track data size
                    try:
                        data_size = len(json.dumps(result.data).encode('utf-8'))
                        self.metrics.track_data_size(data_size)
                    except Exception:
                        pass  # Ignore size tracking errors

            # Store in cache if successful
            if result.success:
                self._store_cache(query, result)
            
            return result
        finally:
            if self.metrics:
                self.metrics.decrement_active_operations()

