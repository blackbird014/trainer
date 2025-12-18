"""
FastAPI service for Stock Mini-App Orchestrator.

Exposes orchestrator endpoints for prompt flow execution.
Run on port 3001/api (integrated with Express server).
"""

import os
import logging
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

