"""Tests for metrics collection."""

import pytest
from format_converter.metrics import MetricsCollector, PROMETHEUS_AVAILABLE


def test_metrics_collector_init():
    """Test metrics collector initialization."""
    collector = MetricsCollector()
    assert collector is not None


@pytest.mark.skipif(not PROMETHEUS_AVAILABLE, reason="Prometheus not available")
def test_track_operation():
    """Test tracking operations."""
    collector = MetricsCollector()
    collector.track_operation("markdown", "html", "success")
    # Should not raise


@pytest.mark.skipif(not PROMETHEUS_AVAILABLE, reason="Prometheus not available")
def test_track_duration():
    """Test tracking duration."""
    collector = MetricsCollector()
    collector.track_duration("markdown", "html", 0.5)
    # Should not raise


@pytest.mark.skipif(not PROMETHEUS_AVAILABLE, reason="Prometheus not available")
def test_track_error():
    """Test tracking errors."""
    collector = MetricsCollector()
    collector.track_error("markdown", "html", "conversion_error")
    # Should not raise

