"""
Prometheus metrics for test-agent module.
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
    test_agent_test_runs_total = Counter(
        "test_agent_test_runs_total",
        "Total number of test runs",
        ["module", "status"]
    )

    test_agent_test_duration_seconds = Histogram(
        "test_agent_test_duration_seconds",
        "Test execution duration in seconds",
        ["module"],
        buckets=[1, 5, 10, 30, 60, 300, 600]
    )

    test_agent_tests_passed_total = Counter(
        "test_agent_tests_passed_total",
        "Total tests passed",
        ["module"]
    )

    test_agent_tests_failed_total = Counter(
        "test_agent_tests_failed_total",
        "Total tests failed",
        ["module"]
    )

    test_agent_coverage_percentage = Gauge(
        "test_agent_coverage_percentage",
        "Test coverage percentage",
        ["module"]
    )

    test_agent_tests_generated_total = Counter(
        "test_agent_tests_generated_total",
        "Total tests generated",
        ["module"]
    )

    test_agent_integration_test_runs_total = Counter(
        "test_agent_integration_test_runs_total",
        "Total integration test runs",
        ["modules"]
    )
else:
    # Dummy metrics if Prometheus not available
    test_agent_test_runs_total = None
    test_agent_test_duration_seconds = None
    test_agent_tests_passed_total = None
    test_agent_tests_failed_total = None
    test_agent_coverage_percentage = None
    test_agent_tests_generated_total = None
    test_agent_integration_test_runs_total = None


class MetricsCollector:
    """Helper class for collecting metrics."""

    def __init__(self):
        """Initialize metrics collector."""
        pass

    def track_test_run(
        self,
        module: str,
        passed: int,
        failed: int,
        skipped: int,
        errors: int,
        duration: float
    ):
        """Track a test run."""
        if not PROMETHEUS_AVAILABLE:
            return

        if test_agent_test_runs_total:
            status = "success" if failed == 0 and errors == 0 else "failure"
            test_agent_test_runs_total.labels(
                module=module,
                status=status
            ).inc()

        if test_agent_test_duration_seconds:
            test_agent_test_duration_seconds.labels(
                module=module
            ).observe(duration)

        if test_agent_tests_passed_total:
            test_agent_tests_passed_total.labels(module=module).inc(passed)

        if test_agent_tests_failed_total:
            test_agent_tests_failed_total.labels(module=module).inc(failed)

    def track_coverage(self, module: str, percentage: float):
        """Track coverage percentage."""
        if PROMETHEUS_AVAILABLE and test_agent_coverage_percentage:
            test_agent_coverage_percentage.labels(module=module).set(percentage)

    def track_test_generation(self, module: str, count: int):
        """Track test generation."""
        if PROMETHEUS_AVAILABLE and test_agent_tests_generated_total:
            test_agent_tests_generated_total.labels(module=module).inc(count)

    def track_integration_test_run(
        self,
        modules: str,
        passed: int,
        failed: int,
        duration: float
    ):
        """Track integration test run."""
        if PROMETHEUS_AVAILABLE and test_agent_integration_test_runs_total:
            test_agent_integration_test_runs_total.labels(modules=modules).inc()

