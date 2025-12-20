"""
Monitoring utilities for trainer mini-apps.

Provides utilities for Prometheus service discovery and monitoring configuration.
"""

from .prometheus_sd import (
    load_services_config,
    create_prometheus_targets,
    format_target_url,
)

__all__ = [
    "load_services_config",
    "create_prometheus_targets",
    "format_target_url",
]

__version__ = "0.1.0"

