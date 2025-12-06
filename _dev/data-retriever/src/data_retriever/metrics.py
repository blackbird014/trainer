"""
Prometheus metrics for data-retriever module.
"""

try:
    from prometheus_client import Counter, Histogram, Gauge
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    Counter = None
    Histogram = None
    Gauge = None

# Metrics (initialized if Prometheus is available)
if PROMETHEUS_AVAILABLE:
    data_retriever_operations_total = Counter(
        "data_retriever_operations_total",
        "Total number of retrieval operations",
        ["source", "status"]
    )
    
    data_retriever_operation_duration_seconds = Histogram(
        "data_retriever_operation_duration_seconds",
        "Retrieval operation duration in seconds",
        ["source"],
        buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0]
    )
    
    data_retriever_cache_hits_total = Counter(
        "data_retriever_cache_hits_total",
        "Total cache hits",
        ["source"]
    )
    
    data_retriever_cache_misses_total = Counter(
        "data_retriever_cache_misses_total",
        "Total cache misses",
        ["source"]
    )
    
    data_retriever_errors_total = Counter(
        "data_retriever_errors_total",
        "Total retrieval errors",
        ["source", "error_type"]
    )
    
    data_retriever_data_size_bytes = Histogram(
        "data_retriever_data_size_bytes",
        "Size of retrieved data in bytes",
        ["source"],
        buckets=[1024, 10240, 102400, 1048576, 10485760, 104857600]  # 1KB to 100MB
    )
    
    data_retriever_active_operations = Gauge(
        "data_retriever_active_operations",
        "Currently active retrieval operations",
        ["source"]
    )
else:
    # Dummy metrics if Prometheus not available
    data_retriever_operations_total = None
    data_retriever_operation_duration_seconds = None
    data_retriever_cache_hits_total = None
    data_retriever_cache_misses_total = None
    data_retriever_errors_total = None
    data_retriever_data_size_bytes = None
    data_retriever_active_operations = None


class MetricsCollector:
    """Helper class for collecting metrics."""
    
    def __init__(self, source_name: str):
        """
        Initialize metrics collector.
        
        Args:
            source_name: Name of the data source
        """
        self.source_name = source_name
    
    def track_operation(self, status: str = "success"):
        """Track a retrieval operation."""
        if PROMETHEUS_AVAILABLE and data_retriever_operations_total:
            data_retriever_operations_total.labels(
                source=self.source_name,
                status=status
            ).inc()
    
    def track_duration(self, duration: float):
        """Track operation duration."""
        if PROMETHEUS_AVAILABLE and data_retriever_operation_duration_seconds:
            data_retriever_operation_duration_seconds.labels(
                source=self.source_name
            ).observe(duration)
    
    def track_cache_hit(self):
        """Track cache hit."""
        if PROMETHEUS_AVAILABLE and data_retriever_cache_hits_total:
            data_retriever_cache_hits_total.labels(
                source=self.source_name
            ).inc()
    
    def track_cache_miss(self):
        """Track cache miss."""
        if PROMETHEUS_AVAILABLE and data_retriever_cache_misses_total:
            data_retriever_cache_misses_total.labels(
                source=self.source_name
            ).inc()
    
    def track_error(self, error_type: str = "unknown"):
        """Track error."""
        if PROMETHEUS_AVAILABLE and data_retriever_errors_total:
            data_retriever_errors_total.labels(
                source=self.source_name,
                error_type=error_type
            ).inc()
    
    def track_data_size(self, size_bytes: int):
        """Track retrieved data size."""
        if PROMETHEUS_AVAILABLE and data_retriever_data_size_bytes:
            data_retriever_data_size_bytes.labels(
                source=self.source_name
            ).observe(size_bytes)
    
    def increment_active_operations(self):
        """Increment active operations counter."""
        if PROMETHEUS_AVAILABLE and data_retriever_active_operations:
            data_retriever_active_operations.labels(
                source=self.source_name
            ).inc()
    
    def decrement_active_operations(self):
        """Decrement active operations counter."""
        if PROMETHEUS_AVAILABLE and data_retriever_active_operations:
            data_retriever_active_operations.labels(
                source=self.source_name
            ).dec()

