"""
Prometheus Service Discovery utilities.

Provides functions for loading service configurations and converting them
to Prometheus HTTP Service Discovery format.
"""

import json
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse


def load_services_config(config_path: Path) -> Dict[str, str]:
    """
    Load services configuration from YAML file.
    
    Expected YAML format:
        services:
          - name: service-name
            url: http://localhost:8000
          - name: another-service
            url: http://localhost:8001
    
    Args:
        config_path: Path to YAML config file
        
    Returns:
        Dict mapping service name to URL, e.g.:
        {'data-store': 'http://localhost:8007', 'llm-provider': 'http://localhost:8001', ...}
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config file format is invalid
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    if not config or 'services' not in config:
        raise ValueError(f"Invalid config format: expected 'services' key in {config_path}")
    
    services_dict = {}
    for service in config['services']:
        if 'name' not in service or 'url' not in service:
            raise ValueError(f"Invalid service entry: must have 'name' and 'url' keys")
        services_dict[service['name']] = service['url']
    
    return services_dict


def format_target_url(url: str) -> str:
    """
    Format URL for Prometheus (strip protocol, extract host:port).
    
    Args:
        url: Full URL like 'http://localhost:8007' or 'https://example.com:443'
        
    Returns:
        Target string like 'localhost:8007' or 'example.com:443'
    """
    parsed = urlparse(url)
    host = parsed.hostname or parsed.netloc.split(':')[0]
    port = parsed.port
    
    # If no port in URL, use default ports based on scheme
    if port is None:
        if parsed.scheme == 'https':
            port = 443
        else:
            port = 80
    
    return f"{host}:{port}"


def create_prometheus_targets(
    services_config: Dict[str, str],
    miniapp_name: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Convert services config to Prometheus HTTP SD format.
    
    Args:
        services_config: Dict of {service_name: url}
        miniapp_name: Optional mini-app name for labeling
        
    Returns:
        List of Prometheus target dicts:
        [
            {
                "targets": ["localhost:8007"],
                "labels": {
                    "job": "data-store",
                    "instance": "data-store-service",
                    "miniapp": "stock-miniapp"  # if miniapp_name provided
                }
            },
            ...
        ]
    """
    targets = []
    
    for service_name, url in services_config.items():
        target_host_port = format_target_url(url)
        
        labels = {
            "job": service_name,
            "instance": f"{service_name}-service",
        }
        
        if miniapp_name:
            labels["miniapp"] = miniapp_name
        
        targets.append({
            "targets": [target_host_port],
            "labels": labels
        })
    
    return targets

