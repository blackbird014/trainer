"""Tests for metrics collection."""

import pytest
from model_trainer.metrics import MetricsCollector, PROMETHEUS_AVAILABLE


def test_metrics_collector_init():
    """Test metrics collector initialization."""
    collector = MetricsCollector()
    assert collector is not None


@pytest.mark.skipif(not PROMETHEUS_AVAILABLE, reason="Prometheus not available")
def test_track_training_run():
    """Test tracking training runs."""
    collector = MetricsCollector()
    collector.track_training_run("huggingface", "success")
    # Should not raise


@pytest.mark.skipif(not PROMETHEUS_AVAILABLE, reason="Prometheus not available")
def test_track_training_duration():
    """Test tracking training duration."""
    collector = MetricsCollector()
    collector.track_training_duration("huggingface", 100.5)
    # Should not raise


@pytest.mark.skipif(not PROMETHEUS_AVAILABLE, reason="Prometheus not available")
def test_track_error():
    """Test tracking errors."""
    collector = MetricsCollector()
    collector.track_error("TrainingError", "huggingface")
    # Should not raise

