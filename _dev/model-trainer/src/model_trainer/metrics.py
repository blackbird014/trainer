"""
Prometheus metrics for model-trainer module.
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
    model_trainer_training_runs_total = Counter(
        "model_trainer_training_runs_total",
        "Total number of training runs",
        ["framework", "status"]
    )

    model_trainer_training_duration_seconds = Histogram(
        "model_trainer_training_duration_seconds",
        "Training duration in seconds",
        ["framework"],
        buckets=[60, 300, 600, 1800, 3600, 7200, 18000]  # 1min to 5hrs
    )

    model_trainer_dataset_size = Histogram(
        "model_trainer_dataset_size",
        "Size of prepared datasets",
        ["dataset_type"],
        buckets=[100, 1000, 10000, 100000, 1000000]
    )

    model_trainer_evaluation_runs_total = Counter(
        "model_trainer_evaluation_runs_total",
        "Total number of evaluation runs",
        ["model_version", "status"]
    )

    model_trainer_model_versions_total = Counter(
        "model_trainer_model_versions_total",
        "Total number of model versions created",
        ["framework"]
    )

    model_trainer_checkpoint_size_bytes = Histogram(
        "model_trainer_checkpoint_size_bytes",
        "Size of model checkpoints in bytes",
        ["framework"],
        buckets=[1048576, 10485760, 104857600, 1073741824]  # 1MB to 1GB
    )

    model_trainer_errors_total = Counter(
        "model_trainer_errors_total",
        "Total training errors",
        ["error_type", "framework"]
    )

    model_trainer_active_training_runs = Gauge(
        "model_trainer_active_training_runs",
        "Number of currently active training runs",
        ["framework"]
    )
else:
    # Dummy metrics if Prometheus not available
    model_trainer_training_runs_total = None
    model_trainer_training_duration_seconds = None
    model_trainer_dataset_size = None
    model_trainer_evaluation_runs_total = None
    model_trainer_model_versions_total = None
    model_trainer_checkpoint_size_bytes = None
    model_trainer_errors_total = None
    model_trainer_active_training_runs = None


class MetricsCollector:
    """Helper class for collecting metrics."""

    def __init__(self):
        """Initialize metrics collector."""
        pass

    def track_training_run(self, framework: str, status: str = "success"):
        """Track a training run."""
        if PROMETHEUS_AVAILABLE and model_trainer_training_runs_total:
            model_trainer_training_runs_total.labels(
                framework=framework,
                status=status
            ).inc()

    def track_training_duration(self, framework: str, duration: float):
        """Track training duration."""
        if PROMETHEUS_AVAILABLE and model_trainer_training_duration_seconds:
            model_trainer_training_duration_seconds.labels(
                framework=framework
            ).observe(duration)

    def track_dataset_size(self, dataset_type: str, size: int):
        """Track dataset size."""
        if PROMETHEUS_AVAILABLE and model_trainer_dataset_size:
            model_trainer_dataset_size.labels(
                dataset_type=dataset_type
            ).observe(size)

    def track_evaluation_run(self, model_version: str, status: str = "success"):
        """Track an evaluation run."""
        if PROMETHEUS_AVAILABLE and model_trainer_evaluation_runs_total:
            model_trainer_evaluation_runs_total.labels(
                model_version=model_version,
                status=status
            ).inc()

    def track_model_version(self, framework: str):
        """Track model version creation."""
        if PROMETHEUS_AVAILABLE and model_trainer_model_versions_total:
            model_trainer_model_versions_total.labels(
                framework=framework
            ).inc()

    def track_checkpoint_size(self, framework: str, size_bytes: int):
        """Track checkpoint size."""
        if PROMETHEUS_AVAILABLE and model_trainer_checkpoint_size_bytes:
            model_trainer_checkpoint_size_bytes.labels(
                framework=framework
            ).observe(size_bytes)

    def track_error(self, error_type: str, framework: str = "unknown"):
        """Track error."""
        if PROMETHEUS_AVAILABLE and model_trainer_errors_total:
            model_trainer_errors_total.labels(
                error_type=error_type,
                framework=framework
            ).inc()

    def set_active_training_runs(self, framework: str, count: int):
        """Set number of active training runs."""
        if PROMETHEUS_AVAILABLE and model_trainer_active_training_runs:
            model_trainer_active_training_runs.labels(
                framework=framework
            ).set(count)

