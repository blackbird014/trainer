"""
Prometheus metrics for data-store module.
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
    data_store_operations_total = Counter(
        "data_store_operations_total",
        "Total number of store operations",
        ["operation", "status"]
    )
    
    data_store_operation_duration_seconds = Histogram(
        "data_store_operation_duration_seconds",
        "Store operation duration in seconds",
        ["operation"],
        buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
    )
    
    data_store_errors_total = Counter(
        "data_store_errors_total",
        "Total store errors",
        ["operation", "error_type"]
    )
    
    data_store_data_size_bytes = Histogram(
        "data_store_data_size_bytes",
        "Size of stored data in bytes",
        ["operation"],
        buckets=[1024, 10240, 102400, 1048576, 10485760, 104857600]  # 1KB to 100MB
    )
    
    data_store_items_total = Gauge(
        "data_store_items_total",
        "Total number of items in store",
        ["backend"]
    )
    
    data_store_active_operations = Gauge(
        "data_store_active_operations",
        "Currently active store operations",
        ["operation"]
    )
else:
    # Dummy metrics if Prometheus not available
    data_store_operations_total = None
    data_store_operation_duration_seconds = None
    data_store_errors_total = None
    data_store_data_size_bytes = None
    data_store_items_total = None
    data_store_active_operations = None


class MetricsCollector:
    """Helper class for collecting metrics."""
    
    def __init__(self, backend: str = "unknown"):
        """
        Initialize metrics collector.
        
        Args:
            backend: Name of the storage backend
        """
        self.backend = backend
    
    def track_operation(self, operation: str, status: str = "success"):
        """Track a store operation."""
        if PROMETHEUS_AVAILABLE and data_store_operations_total:
            data_store_operations_total.labels(
                operation=operation,
                status=status
            ).inc()
    
    def track_duration(self, operation: str, duration: float):
        """Track operation duration."""
        if PROMETHEUS_AVAILABLE and data_store_operation_duration_seconds:
            data_store_operation_duration_seconds.labels(
                operation=operation
            ).observe(duration)
    
    def track_error(self, operation: str, error_type: str = "unknown"):
        """Track error."""
        if PROMETHEUS_AVAILABLE and data_store_errors_total:
            data_store_errors_total.labels(
                operation=operation,
                error_type=error_type
            ).inc()
    
    def track_data_size(self, operation: str, size_bytes: int):
        """Track data size."""
        if PROMETHEUS_AVAILABLE and data_store_data_size_bytes:
            data_store_data_size_bytes.labels(
                operation=operation
            ).observe(size_bytes)
    
    def update_item_count(self, count: int):
        """Update total item count."""
        if PROMETHEUS_AVAILABLE and data_store_items_total:
            data_store_items_total.labels(backend=self.backend).set(count)
    
    def increment_active_operations(self, operation: str):
        """Increment active operations counter."""
        if PROMETHEUS_AVAILABLE and data_store_active_operations:
            data_store_active_operations.labels(
                operation=operation
            ).inc()
    
    def decrement_active_operations(self, operation: str):
        """Decrement active operations counter."""
        if PROMETHEUS_AVAILABLE and data_store_active_operations:
            data_store_active_operations.labels(
                operation=operation
            ).dec()

