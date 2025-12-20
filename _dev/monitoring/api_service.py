"""
Standalone Monitoring Service for Prometheus Service Discovery.

Polls mini-apps periodically to discover services and aggregates them
for Prometheus HTTP Service Discovery.
"""

import asyncio
import hashlib
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

import httpx
import yaml
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Monitoring Service",
    description="Service discovery for Prometheus HTTP SD",
    version="0.1.0"
)

# Global cache structure: {miniapp_url: {"hash": "...", "targets": [...], "last_update": timestamp}}
cache: Dict[str, Dict[str, Any]] = {}

# Configuration
CONFIG_PATH = Path(__file__).parent / "config.yml"
POLLING_INTERVAL = 30  # seconds
MINIAPPS: List[Dict[str, str]] = []


def load_config() -> Dict[str, Any]:
    """Load configuration from YAML file or environment variables."""
    config = {
        "miniapps": [],
        "polling_interval": 30,
        "port": 8008
    }
    
    # Load from file if exists
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r') as f:
            file_config = yaml.safe_load(f) or {}
            config.update(file_config)
    
    # Override with environment variables
    if os.getenv("MONITORING_PORT"):
        config["port"] = int(os.getenv("MONITORING_PORT"))
    
    if os.getenv("POLLING_INTERVAL"):
        config["polling_interval"] = int(os.getenv("POLLING_INTERVAL"))
    
    return config


def compute_hash(data: Any) -> str:
    """Compute SHA256 hash of data (for change detection)."""
    json_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(json_str.encode()).hexdigest()


async def poll_miniapp(miniapp_url: str, miniapp_name: str) -> Optional[List[Dict[str, Any]]]:
    """
    Poll a mini-app for its service targets.
    
    Returns:
        List of target dicts if successful, None if failed
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{miniapp_url}/monitoring/targets")
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(
                    f"Mini-app {miniapp_name} ({miniapp_url}) returned status {response.status_code}"
                )
                return None
    except httpx.TimeoutException:
        logger.warning(f"Timeout polling mini-app {miniapp_name} ({miniapp_url})")
        return None
    except Exception as e:
        logger.warning(f"Error polling mini-app {miniapp_name} ({miniapp_url}): {e}")
        return None


async def poll_and_update_cache():
    """Poll all mini-apps and update cache if changed."""
    logger.debug("Starting polling cycle")
    
    for miniapp in MINIAPPS:
        miniapp_url = miniapp["url"]
        miniapp_name = miniapp["name"]
        
        targets = await poll_miniapp(miniapp_url, miniapp_name)
        
        if targets is not None:
            # Compute hash of new targets
            new_hash = compute_hash(targets)
            
            # Check if changed
            if miniapp_url not in cache or cache[miniapp_url]["hash"] != new_hash:
                cache[miniapp_url] = {
                    "hash": new_hash,
                    "targets": targets,
                    "last_update": datetime.now().isoformat(),
                    "miniapp_name": miniapp_name,
                    "status": "reachable"
                }
                logger.info(f"Updated cache for {miniapp_name} ({miniapp_url})")
            else:
                # Update timestamp even if unchanged
                cache[miniapp_url]["last_update"] = datetime.now().isoformat()
                cache[miniapp_url]["status"] = "reachable"
        else:
            # Keep last known good cache, but mark as unreachable
            if miniapp_url in cache:
                cache[miniapp_url]["status"] = "unreachable"
            else:
                # First time and unreachable - don't cache yet
                logger.warning(
                    f"Mini-app {miniapp_name} ({miniapp_url}) is unreachable and has no cached data"
                )


async def poll_miniapps_periodically():
    """Periodic polling task (runs forever)."""
    while True:
        try:
            await poll_and_update_cache()
        except Exception as e:
            logger.error(f"Error in polling cycle: {e}", exc_info=True)
        
        await asyncio.sleep(POLLING_INTERVAL)


@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    global MINIAPPS, POLLING_INTERVAL
    
    logger.info("Starting Monitoring Service")
    
    # Load configuration
    config = load_config()
    MINIAPPS = config.get("miniapps", [])
    POLLING_INTERVAL = config.get("polling_interval", 30)
    
    logger.info(f"Loaded {len(MINIAPPS)} mini-app(s) from configuration")
    logger.info(f"Polling interval: {POLLING_INTERVAL} seconds")
    
    # Initial poll
    logger.info("Performing initial poll...")
    await poll_and_update_cache()
    
    # Start periodic polling
    asyncio.create_task(poll_miniapps_periodically())
    logger.info("Periodic polling task started")


@app.get("/")
async def root():
    """API information."""
    return {
        "name": "Monitoring Service",
        "version": "0.1.0",
        "endpoints": {
            "targets": "GET /monitoring/targets",
            "health": "GET /monitoring/health",
            "refresh": "POST /monitoring/refresh",
            "refresh_miniapp": "POST /monitoring/refresh/{miniapp_url}",
        },
        "miniapps": len(MINIAPPS),
        "cached_targets": sum(len(cache[url]["targets"]) for url in cache if "targets" in cache[url])
    }


@app.get("/monitoring/targets")
async def get_monitoring_targets():
    """
    Returns Prometheus HTTP SD format targets aggregated from all mini-apps.
    """
    # Aggregate all targets from cache
    all_targets = []
    
    for miniapp_url, cache_entry in cache.items():
        if "targets" in cache_entry and cache_entry.get("status") == "reachable":
            all_targets.extend(cache_entry["targets"])
    
    return all_targets


@app.get("/monitoring/health")
async def get_health():
    """
    Health check endpoint showing mini-app reachability status.
    """
    health_status = {
        "status": "healthy",
        "miniapps": []
    }
    
    for miniapp in MINIAPPS:
        miniapp_url = miniapp["url"]
        miniapp_name = miniapp["name"]
        
        if miniapp_url in cache:
            cache_entry = cache[miniapp_url]
            health_status["miniapps"].append({
                "name": miniapp_name,
                "url": miniapp_url,
                "status": cache_entry.get("status", "unknown"),
                "last_update": cache_entry.get("last_update"),
                "targets_count": len(cache_entry.get("targets", []))
            })
        else:
            health_status["miniapps"].append({
                "name": miniapp_name,
                "url": miniapp_url,
                "status": "not_polled",
                "last_update": None,
                "targets_count": 0
            })
    
    # Overall status is healthy if at least one mini-app is reachable
    if not any(m.get("status") == "reachable" for m in health_status["miniapps"]):
        health_status["status"] = "degraded"
    
    return health_status


class RefreshResponse(BaseModel):
    success: bool
    message: str
    miniapp_url: Optional[str] = None


@app.post("/monitoring/refresh", response_model=RefreshResponse)
async def refresh_all():
    """
    Force refresh of all mini-app caches.
    """
    logger.info("Forcing refresh of all mini-apps")
    await poll_and_update_cache()
    
    return RefreshResponse(
        success=True,
        message=f"Refreshed all {len(MINIAPPS)} mini-app(s)"
    )


@app.post("/monitoring/refresh/{miniapp_url:path}", response_model=RefreshResponse)
async def refresh_miniapp(miniapp_url: str):
    """
    Force refresh of a specific mini-app cache.
    
    Note: URL should be URL-encoded if needed (e.g., http%3A%2F%2Flocalhost%3A3003)
    """
    # Find the mini-app
    miniapp_entry = None
    for miniapp in MINIAPPS:
        if miniapp["url"] == miniapp_url:
            miniapp_entry = miniapp
            break
    
    if not miniapp_entry:
        raise HTTPException(
            status_code=404,
            detail=f"Mini-app with URL {miniapp_url} not found in configuration"
        )
    
    logger.info(f"Forcing refresh of mini-app {miniapp_entry['name']} ({miniapp_url})")
    targets = await poll_miniapp(miniapp_url, miniapp_entry["name"])
    
    if targets is not None:
        new_hash = compute_hash(targets)
        cache[miniapp_url] = {
            "hash": new_hash,
            "targets": targets,
            "last_update": datetime.now().isoformat(),
            "miniapp_name": miniapp_entry["name"],
            "status": "reachable"
        }
        return RefreshResponse(
            success=True,
            message=f"Refreshed mini-app {miniapp_entry['name']}",
            miniapp_url=miniapp_url
        )
    else:
        # Keep existing cache but mark as unreachable
        if miniapp_url in cache:
            cache[miniapp_url]["status"] = "unreachable"
        return RefreshResponse(
            success=False,
            message=f"Failed to refresh mini-app {miniapp_entry['name']} (unreachable)",
            miniapp_url=miniapp_url
        )


if __name__ == "__main__":
    import uvicorn
    
    config = load_config()
    port = config.get("port", 8008)
    
    print("=" * 80)
    print("Monitoring Service")
    print("=" * 80)
    print()
    print(f"Starting server on http://0.0.0.0:{port}")
    print()
    print("Endpoints:")
    print(f"  - http://localhost:{port}/                    - API info")
    print(f"  - http://localhost:{port}/docs                - Swagger UI")
    print(f"  - http://localhost:{port}/monitoring/targets  - Prometheus HTTP SD")
    print(f"  - http://localhost:{port}/monitoring/health   - Health check")
    print(f"  - http://localhost:{port}/monitoring/refresh  - Force refresh (POST)")
    print()
    print("=" * 80)
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=port)

