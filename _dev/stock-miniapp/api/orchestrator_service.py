"""
FastAPI service for Stock Mini-App Orchestrator.

Exposes orchestrator endpoints for prompt flow execution.
Run on port 3001/api (integrated with Express server).
"""

import os
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import httpx

from orchestrator import PromptOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import monitoring utilities
try:
    from monitoring.prometheus_sd import create_prometheus_targets, load_services_config
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False
    logger.warning("Monitoring library not available. Install with: pip install -e ../../monitoring")

# Initialize FastAPI app
app = FastAPI(
    title="Stock Mini-App Orchestrator API",
    description="Orchestrates prompt flow for stock analysis",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = PromptOrchestrator()

# Request/Response models
class PromptRunRequest(BaseModel):
    ticker: str


class PromptRunResponse(BaseModel):
    success: bool
    run_id: str
    ticker: str
    html_url: Optional[str] = None
    md_url: Optional[str] = None
    json_url: Optional[str] = None
    status: str
    error: Optional[str] = None


# Routes
@app.get("/")
async def root():
    """API information."""
    return {
        "name": "Stock Mini-App Orchestrator API",
        "version": "0.1.0",
        "endpoints": {
            "run": "POST /prompt/run",
            "html": "GET /prompt/run/{run_id}/html",
            "md": "GET /prompt/run/{run_id}/md",
            "json": "GET /prompt/run/{run_id}/json",
        }
    }


@app.post("/prompt/run", response_model=PromptRunResponse)
async def run_prompt_flow(request: PromptRunRequest):
    """
    Orchestrate prompt flow for a ticker.
    
    Request: {ticker: "AAPL"}
    Response: {run_id, ticker, html_url, status}
    """
    try:
        result = await orchestrator.run_prompt_flow(request.ticker)
        return PromptRunResponse(**result)
    except Exception as e:
        logger.error(f"Error in prompt flow: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/prompt/run/{run_id}/html", response_class=HTMLResponse)
async def get_html_result(run_id: str):
    """Retrieve HTML result. All logs include run_id for traceability."""
    logger.info(f"Retrieving HTML result", extra={"run_id": run_id})
    
    try:
        async with httpx.AsyncClient() as client:
            query_response = await client.post(
                f"{orchestrator.data_store_url}/query",
                json={
                    "collection": "prompt_runs",
                    "filters": {"run_id": run_id},  # MongoDB store searches both metadata.run_id and data.run_id
                    "limit": 1
                }
            )
            
            if query_response.status_code != 200:
                logger.error(f"Failed to query data-store", extra={"run_id": run_id})
                raise HTTPException(status_code=500, detail="Failed to retrieve prompt run")
            
            items = query_response.json().get("items", [])
            if not items:
                logger.warning(f"Prompt run not found", extra={"run_id": run_id})
                raise HTTPException(status_code=404, detail=f"Prompt run {run_id} not found")
            
            html_content = items[0].get("data", {}).get("llm_response_html")
            if not html_content:
                logger.warning(f"HTML content not available", extra={"run_id": run_id})
                raise HTTPException(status_code=404, detail=f"HTML not available for run {run_id}")
            
            logger.info(f"HTML retrieved successfully", extra={"run_id": run_id})
            return HTMLResponse(content=html_content)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error retrieving HTML: {str(e)}",
            extra={"run_id": run_id},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/prompt/run/{run_id}/md", response_class=PlainTextResponse)
async def get_md_result(run_id: str):
    """Retrieve Markdown result."""
    logger.info(f"Retrieving Markdown result", extra={"run_id": run_id})
    
    try:
        async with httpx.AsyncClient() as client:
            query_response = await client.post(
                f"{orchestrator.data_store_url}/query",
                json={
                    "collection": "prompt_runs",
                    "filters": {"run_id": run_id},  # MongoDB store searches both metadata.run_id and data.run_id
                    "limit": 1
                }
            )
            
            if query_response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to retrieve prompt run")
            
            items = query_response.json().get("items", [])
            if not items:
                raise HTTPException(status_code=404, detail=f"Prompt run {run_id} not found")
            
            md_content = items[0].get("data", {}).get("llm_response_md")
            if not md_content:
                raise HTTPException(status_code=404, detail=f"Markdown not available for run {run_id}")
            
            return PlainTextResponse(content=md_content, media_type="text/markdown")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving Markdown: {str(e)}", extra={"run_id": run_id}, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/prompt/run/{run_id}/json", response_class=JSONResponse)
async def get_json_result(run_id: str):
    """Retrieve JSON result."""
    logger.info(f"Retrieving JSON result", extra={"run_id": run_id})
    
    try:
        async with httpx.AsyncClient() as client:
            query_response = await client.post(
                f"{orchestrator.data_store_url}/query",
                json={
                    "collection": "prompt_runs",
                    "filters": {"run_id": run_id},  # MongoDB store searches both metadata.run_id and data.run_id
                    "limit": 1
                }
            )
            
            if query_response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to retrieve prompt run")
            
            items = query_response.json().get("items", [])
            if not items:
                raise HTTPException(status_code=404, detail=f"Prompt run {run_id} not found")
            
            json_content = items[0].get("data", {}).get("llm_response_json")
            if not json_content:
                raise HTTPException(status_code=404, detail=f"JSON not available for run {run_id}")
            
            return JSONResponse(content=json_content)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving JSON: {str(e)}", extra={"run_id": run_id}, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/monitoring/targets")
async def get_monitoring_targets():
    """
    Returns Prometheus HTTP SD format targets for this mini-app's services.
    
    Requires monitoring library to be installed:
    pip install -e ../../monitoring
    """
    if not MONITORING_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Monitoring library not available. Install with: pip install -e ../../monitoring"
        )
    
    try:
        # Load configuration from YAML file
        config_path = Path(__file__).parent / "monitoring_config.yaml"
        services_config = load_services_config(config_path)
        
        # Convert to Prometheus format
        targets = create_prometheus_targets(services_config, miniapp_name="stock-miniapp")
        
        return targets
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail=f"Monitoring configuration file not found: monitoring_config.yaml"
        )
    except Exception as e:
        logger.error(f"Error generating monitoring targets: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/monitoring/test")
async def test_monitoring():
    """
    Test endpoint for monitoring functionality.
    Returns status of monitoring integration and test results.
    """
    result = {
        "monitoring_available": MONITORING_AVAILABLE,
        "status": "ok",
        "tests": {}
    }
    
    if not MONITORING_AVAILABLE:
        result["status"] = "error"
        result["error"] = "Monitoring library not available. Install with: pip install -e ../../monitoring"
        return result
    
    # Test 1: Check config file exists
    config_path = Path(__file__).parent / "monitoring_config.yaml"
    result["tests"]["config_file_exists"] = config_path.exists()
    
    if not config_path.exists():
        result["status"] = "error"
        result["error"] = f"Monitoring configuration file not found: monitoring_config.yaml"
        return result
    
    # Test 2: Load and parse config
    try:
        services_config = load_services_config(config_path)
        result["tests"]["config_load"] = True
        result["tests"]["services_count"] = len(services_config)
        result["tests"]["services"] = list(services_config.keys())
    except Exception as e:
        result["status"] = "error"
        result["tests"]["config_load"] = False
        result["error"] = f"Failed to load config: {str(e)}"
        return result
    
    # Test 3: Generate targets
    try:
        targets = create_prometheus_targets(services_config, miniapp_name="stock-miniapp")
        result["tests"]["targets_generation"] = True
        result["tests"]["targets_count"] = len(targets)
        result["tests"]["targets"] = targets
    except Exception as e:
        result["status"] = "error"
        result["tests"]["targets_generation"] = False
        result["error"] = f"Failed to generate targets: {str(e)}"
        return result
    
    # Test 4: Try to reach monitoring service (if available)
    monitoring_url = os.getenv("MONITORING_SERVICE_URL", "http://localhost:8008")
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            health_response = await client.get(f"{monitoring_url}/monitoring/health")
            if health_response.status_code == 200:
                result["tests"]["monitoring_service_reachable"] = True
                result["tests"]["monitoring_service_health"] = health_response.json()
            else:
                result["tests"]["monitoring_service_reachable"] = False
                result["tests"]["monitoring_service_error"] = f"Status {health_response.status_code}"
    except Exception as e:
        result["tests"]["monitoring_service_reachable"] = False
        result["tests"]["monitoring_service_error"] = str(e)
    
    return result


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 3002))  # Different port from Express (3001)
    
    print("=" * 80)
    print("Stock Mini-App Orchestrator FastAPI Service")
    print("=" * 80)
    print()
    print(f"Starting server on http://0.0.0.0:{port}")
    print()
    print("Endpoints:")
    print(f"  - http://localhost:{port}/              - API info")
    print(f"  - http://localhost:{port}/docs          - Swagger UI")
    print(f"  - http://localhost:{port}/prompt/run   - Run prompt flow")
    print()
    print("=" * 80)
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=port)

