"""
FastAPI service for data-retriever module.

Exposes data retrieval functionality via REST API and Prometheus metrics.
Run on port 8003 (configurable).
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

try:
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

from data_retriever import (
    FileRetriever,
    APIRetriever,
    YahooFinanceRetriever,
    SECRetriever,
    DatabaseRetriever,
    DataCache,
)

# Initialize FastAPI app
app = FastAPI(
    title="Data Retriever API",
    description="Microservice for data retrieval operations",
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

# Initialize cache (optional)
cache = DataCache(default_ttl=3600, max_size=1000) if os.getenv("ENABLE_CACHE", "true").lower() == "true" else None

# Initialize retrievers
retrievers = {
    "file": FileRetriever(cache=cache, enable_metrics=True),
    "api": APIRetriever(cache=cache, enable_metrics=True),
}

# Optional retrievers
try:
    retrievers["yahoo_finance"] = YahooFinanceRetriever(cache=cache, enable_metrics=True)
except Exception:
    pass

try:
    retrievers["sec"] = SECRetriever(cache=cache, enable_metrics=True)
except Exception:
    pass


# Request/Response models
class RetrieveRequest(BaseModel):
    source: str
    query: Dict[str, Any]


class RetrieveResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    source: str
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# Routes
@app.get("/")
async def root():
    """API information."""
    return {
        "name": "Data Retriever API",
        "version": "0.1.0",
        "endpoints": {
            "retrieve": "/retrieve",
            "metrics": "/metrics",
            "health": "/health",
            "sources": "/sources",
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "data-retriever"}


@app.get("/sources")
async def list_sources():
    """List available data sources."""
    return {
        "sources": list(retrievers.keys()),
        "count": len(retrievers)
    }


@app.post("/retrieve", response_model=RetrieveResponse)
async def retrieve(request: RetrieveRequest):
    """Retrieve data from a source."""
    if request.source not in retrievers:
        raise HTTPException(
            status_code=404,
            detail=f"Source '{request.source}' not found. Available sources: {list(retrievers.keys())}"
        )
    
    retriever = retrievers[request.source]
    result = retriever.retrieve_with_cache(request.query)
    
    if result.success:
        return RetrieveResponse(
            success=True,
            data=result.data,
            source=result.source,
            metadata=result.metadata,
        )
    else:
        return RetrieveResponse(
            success=False,
            source=result.source,
            error=result.error,
            metadata=result.metadata,
        )


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Prometheus metrics endpoint."""
    if not PROMETHEUS_AVAILABLE:
        return "# Prometheus client not available\n", 503
    
    return generate_latest()


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8003))
    
    print("=" * 80)
    print("Data Retriever FastAPI Service")
    print("=" * 80)
    print()
    print(f"Starting server on http://0.0.0.0:{port}")
    print()
    print("Endpoints:")
    print(f"  - http://localhost:{port}/              - API info")
    print(f"  - http://localhost:{port}/docs          - Swagger UI")
    print(f"  - http://localhost:{port}/metrics       - Prometheus metrics")
    print(f"  - http://localhost:{port}/health         - Health check")
    print(f"  - http://localhost:{port}/sources        - List sources")
    print(f"  - http://localhost:{port}/retrieve      - Retrieve data")
    print()
    print("Available Sources:")
    for source in retrievers.keys():
        print(f"  - {source}")
    print()
    print("Metrics:")
    print("  - data_retriever_operations_total")
    print("  - data_retriever_operation_duration_seconds")
    print("  - data_retriever_cache_hits_total")
    print("  - data_retriever_cache_misses_total")
    print("  - data_retriever_errors_total")
    print("  - data_retriever_data_size_bytes")
    print()
    print("=" * 80)
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=port)

