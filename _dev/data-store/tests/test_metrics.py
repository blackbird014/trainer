"""
Tests for metrics collection.
"""

import pytest
from data_store.metrics import MetricsCollector, PROMETHEUS_AVAILABLE


def test_metrics_collector():
    """Test metrics collector initialization."""
    collector = MetricsCollector(backend="test")
    assert collector.backend == "test"


def test_metrics_operations():
    """Test tracking operations."""
    collector = MetricsCollector(backend="test")
    
    # These should not raise errors even if Prometheus is not available
    collector.track_operation("store", "success")
    collector.track_duration("store", 0.1)
    collector.track_error("store", "ValueError")
    collector.track_data_size("store", 1024)
    collector.update_item_count(10)
    collector.increment_active_operations("store")
    collector.decrement_active_operations("store")


@pytest.mark.skipif(not PROMETHEUS_AVAILABLE, reason="Prometheus not available")
def test_metrics_with_prometheus():
    """Test metrics with Prometheus available."""
    collector = MetricsCollector(backend="test")
    
    # Track operations
    collector.track_operation("store", "success")
    collector.track_duration("store", 0.1)
    
    # Verify metrics exist
    from data_store.metrics import data_store_operations_total
    assert data_store_operations_total is not None

