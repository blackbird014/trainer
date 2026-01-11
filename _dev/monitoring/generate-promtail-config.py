#!/usr/bin/env python3
"""
Generate Promtail configuration from mini-app log-sources.yml files.

Reads config.yml to get list of mini-apps, then aggregates log sources
from each mini-app's log-sources.yml file.
"""

import yaml
import os
import sys
from pathlib import Path
from typing import Dict, List, Any

# Get script directory
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent

def load_config() -> Dict[str, Any]:
    """Load monitoring config.yml to get list of mini-apps."""
    config_path = SCRIPT_DIR / "config.yml"
    if not config_path.exists():
        print(f"Error: config.yml not found at {config_path}", file=sys.stderr)
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f) or {}

def load_log_sources(miniapp_name: str) -> List[Dict[str, Any]]:
    """Load log-sources.yml from a mini-app directory."""
    # Try different possible locations for mini-app
    possible_paths = [
        PROJECT_ROOT / "_dev" / miniapp_name / "log-sources.yml",
        PROJECT_ROOT / miniapp_name / "log-sources.yml",
    ]
    
    for log_sources_path in possible_paths:
        if log_sources_path.exists():
            with open(log_sources_path, 'r') as f:
                data = yaml.safe_load(f) or {}
                return data.get('log_sources', [])
    
    print(f"Warning: log-sources.yml not found for mini-app: {miniapp_name}", file=sys.stderr)
    return []

def resolve_path(path_str: str, miniapp_name: str) -> Path:
    """Resolve relative path to absolute path."""
    # If already absolute, use as is
    if os.path.isabs(path_str):
        return Path(path_str)
    
    # Try relative to mini-app directory
    miniapp_dir = PROJECT_ROOT / "_dev" / miniapp_name
    if not miniapp_dir.exists():
        miniapp_dir = PROJECT_ROOT / miniapp_name
    
    resolved = (miniapp_dir / path_str).resolve()
    return resolved

def generate_promtail_config() -> Dict[str, Any]:
    """Generate Promtail configuration from all mini-app log sources."""
    config = load_config()
    miniapps = config.get('miniapps', [])
    
    if not miniapps:
        print("Warning: No mini-apps found in config.yml", file=sys.stderr)
        return create_empty_promtail_config()
    
    scrape_configs = []
    server_config = {
        "http_listen_port": 9080,
        "grpc_listen_port": 0
    }
    
    positions_config = {
        "filename": "/tmp/positions.yaml"
    }
    
    clients_config = [{
        "url": "http://loki:3100/loki/api/v1/push"
    }]
    
    # Aggregate log sources from all mini-apps
    # Group by job name to create scrape configs
    job_configs: Dict[str, Dict[str, Any]] = {}
    
    for miniapp in miniapps:
        miniapp_name = miniapp.get('name', '')
        if not miniapp_name:
            continue
        
        log_sources = load_log_sources(miniapp_name)
        
        for source in log_sources:
            source_name = source.get('name', 'unknown')
            path = source.get('path', '')
            labels = source.get('labels', {})
            patterns = source.get('patterns', ['*.log'])
            
            if not path:
                continue
            
            # Resolve path to absolute host path
            abs_path = resolve_path(path, miniapp_name)
            
            # Convert to container path (relative to mount point)
            # We'll mount logs under /host-dev/logs, so convert _dev/stock-miniapp/logs -> /host-dev/stock-miniapp/logs
            container_base = "/host-dev"
            host_path_str = str(abs_path)
            # Extract relative path from _dev/
            if "_dev/" in host_path_str:
                rel_path = host_path_str.split("_dev/", 1)[1]
                container_path = f"{container_base}/{rel_path}"
            else:
                # Fallback: use last component
                container_path = f"{container_base}/{abs_path.name}"
            
            # Initialize job config if not exists
            if source_name not in job_configs:
                job_configs[source_name] = {
                    "job_name": source_name,
                    "static_configs": [],
                    "labels": labels.copy()
                }
            
            # Build path pattern for Promtail
            # If it's a directory, create entries for each pattern (specific files)
            if abs_path.is_dir():
                # For each pattern, create a separate static_config entry with full file path
                for pattern in patterns:
                    # Check if pattern is a specific filename (not a wildcard)
                    if "*" not in pattern:
                        # Specific file: use full path
                        path_pattern = f"{container_path}/{pattern}"
                    else:
                        # Wildcard pattern: use as is
                        path_pattern = f"{container_path}/{pattern}"
                    
                    job_configs[source_name]["static_configs"].append({
                        "targets": ["localhost"],  # Dummy target, Promtail ignores this for file targets
                        "labels": {
                            **labels,
                            "__path__": path_pattern  # This tells Promtail where to find files
                        }
                    })
            else:
                # Single file path (not a directory)
                job_configs[source_name]["static_configs"].append({
                    "targets": ["localhost"],
                    "labels": {
                        **labels,
                        "__path__": container_path
                    }
                })
    
    # Convert to scrape_configs list
    for job_name, config in job_configs.items():
        scrape_config = {
            "job_name": config["job_name"],
            "static_configs": config["static_configs"]
        }
        scrape_configs.append(scrape_config)
    
    promtail_config = {
        "server": server_config,
        "positions": positions_config,
        "clients": clients_config,
        "scrape_configs": scrape_configs
    }
    
    return promtail_config

def create_empty_promtail_config() -> Dict[str, Any]:
    """Create empty Promtail config structure."""
    return {
        "server": {
            "http_listen_port": 9080,
            "grpc_listen_port": 0
        },
        "positions": {
            "filename": "/tmp/positions.yaml"
        },
        "clients": [
            {
                "- url": "http://loki:3100/loki/api/v1/push"
            }
        ],
        "scrape_configs": []
    }

def main():
    """Main entry point."""
    promtail_config = generate_promtail_config()
    
    output_path = SCRIPT_DIR / "promtail-config.yml"
    with open(output_path, 'w') as f:
        yaml.dump(promtail_config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"Generated promtail-config.yml at {output_path}")
    print(f"Found {len(promtail_config.get('scrape_configs', []))} scrape config(s)")

if __name__ == "__main__":
    main()

