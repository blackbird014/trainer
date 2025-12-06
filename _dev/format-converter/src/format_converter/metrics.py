"""
Prometheus metrics for format-converter module.
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
    format_converter_operations_total = Counter(
        "format_converter_operations_total",
        "Total number of conversion operations",
        ["source_format", "target_format", "status"]
    )

    format_converter_operation_duration_seconds = Histogram(
        "format_converter_operation_duration_seconds",
        "Conversion operation duration in seconds",
        ["source_format", "target_format"],
        buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0]
    )

    format_converter_data_size_bytes = Histogram(
        "format_converter_data_size_bytes",
        "Size of converted data in bytes",
        ["source_format", "target_format"],
        buckets=[1024, 10240, 102400, 1048576, 10485760]  # 1KB to 10MB
    )

    format_converter_errors_total = Counter(
        "format_converter_errors_total",
        "Total conversion errors",
        ["source_format", "target_format", "error_type"]
    )

    format_converter_auto_detections_total = Counter(
        "format_converter_auto_detections_total",
        "Total auto-detection operations",
        ["detected_format"]
    )
else:
    # Dummy metrics if Prometheus not available
    format_converter_operations_total = None
    format_converter_operation_duration_seconds = None
    format_converter_data_size_bytes = None
    format_converter_errors_total = None
    format_converter_auto_detections_total = None


class MetricsCollector:
    """Helper class for collecting metrics."""

    def __init__(self):
        """Initialize metrics collector."""
        pass

    def track_operation(self, source_format: str, target_format: str, status: str = "success"):
        """Track a conversion operation."""
        if PROMETHEUS_AVAILABLE and format_converter_operations_total:
            format_converter_operations_total.labels(
                source_format=source_format,
                target_format=target_format,
                status=status
            ).inc()

    def track_duration(self, source_format: str, target_format: str, duration: float):
        """Track operation duration."""
        if PROMETHEUS_AVAILABLE and format_converter_operation_duration_seconds:
            format_converter_operation_duration_seconds.labels(
                source_format=source_format,
                target_format=target_format
            ).observe(duration)

    def track_data_size(self, source_format: str, target_format: str, size_bytes: int):
        """Track converted data size."""
        if PROMETHEUS_AVAILABLE and format_converter_data_size_bytes:
            format_converter_data_size_bytes.labels(
                source_format=source_format,
                target_format=target_format
            ).observe(size_bytes)

    def track_error(self, source_format: str, target_format: str, error_type: str = "unknown"):
        """Track error."""
        if PROMETHEUS_AVAILABLE and format_converter_errors_total:
            format_converter_errors_total.labels(
                source_format=source_format,
                target_format=target_format,
                error_type=error_type
            ).inc()

    def track_auto_detection(self, detected_format: str):
        """Track auto-detection."""
        if PROMETHEUS_AVAILABLE and format_converter_auto_detections_total:
            format_converter_auto_detections_total.labels(
                detected_format=detected_format
            ).inc()

