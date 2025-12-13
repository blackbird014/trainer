"""
FastAPI service for data-store module.

Exposes data storage functionality via REST API and Prometheus metrics.
Run on port 8007 (configurable).
"""

import os
import time
from datetime import datetime
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

from data_store import create_store, DataStore
from data_store.models import StoredData, QueryResult, LoadResult
from data_store.config import StoreConfig
from data_store.metrics import MetricsCollector
from data_store.utils.company_generator import generate_batch

# Initialize FastAPI app
app = FastAPI(
    title="Data Store API",
    description="Microservice for data persistence operations",
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

# Initialize store from configuration
config = StoreConfig()
store: DataStore = create_store(config.backend, **config.config)
metrics_collector = MetricsCollector(backend=config.backend)


# Request/Response models
class StoreRequest(BaseModel):
    key: str
    data: Any
    metadata: Optional[Dict[str, Any]] = None
    ttl: Optional[int] = None


class UpdateRequest(BaseModel):
    data: Any
    metadata: Optional[Dict[str, Any]] = None


class QueryRequest(BaseModel):
    filters: Dict[str, Any]
    limit: Optional[int] = None
    sort: Optional[Dict[str, int]] = None
    offset: int = 0


class BulkStoreRequest(BaseModel):
    items: List[Dict[str, Any]]


class SeedCompaniesRequest(BaseModel):
    """Request model for seeding companies."""
    count: int = 100
    collection: str = "seed_companies"


# Routes
@app.get("/")
async def root():
    """API information."""
    return {
        "name": "Data Store API",
        "version": "0.1.0",
        "backend": config.backend,
        "endpoints": {
            "store": "/store",
            "retrieve": "/retrieve/{key}",
            "update": "/update/{key}",
            "delete": "/delete/{key}",
            "exists": "/exists/{key}",
            "query": "/query",
            "bulk_store": "/bulk_store",
            "count": "/count",
            "distinct": "/distinct/{field}",
            "metrics": "/metrics",
            "health": "/health",
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    try:
        # Test store connection
        test_key = "__health_check__"
        store.store(test_key, {"test": True}, ttl=1)
        store.delete(test_key)
        return {"status": "healthy", "service": "data-store", "backend": config.backend}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )


@app.post("/store")
async def store_data(request: StoreRequest):
    """Store data."""
    start_time = time.time()
    metrics_collector.increment_active_operations("store")
    
    try:
        key = store.store(
            key=request.key,
            data=request.data,
            metadata=request.metadata,
            ttl=request.ttl
        )
        
        duration = time.time() - start_time
        metrics_collector.track_operation("store", "success")
        metrics_collector.track_duration("store", duration)
        
        return {
            "success": True,
            "key": key,
            "message": "Data stored successfully"
        }
    except Exception as e:
        duration = time.time() - start_time
        metrics_collector.track_operation("store", "error")
        metrics_collector.track_error("store", type(e).__name__)
        metrics_collector.track_duration("store", duration)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        metrics_collector.decrement_active_operations("store")


@app.get("/retrieve/{key}")
async def retrieve_data(key: str):
    """Retrieve data by key."""
    start_time = time.time()
    metrics_collector.increment_active_operations("retrieve")
    
    try:
        stored = store.retrieve(key)
        
        duration = time.time() - start_time
        metrics_collector.track_operation("retrieve", "success" if stored else "not_found")
        metrics_collector.track_duration("retrieve", duration)
        
        if not stored:
            raise HTTPException(status_code=404, detail=f"Key '{key}' not found")
        
        return {
            "success": True,
            "data": stored.dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        duration = time.time() - start_time
        metrics_collector.track_operation("retrieve", "error")
        metrics_collector.track_error("retrieve", type(e).__name__)
        metrics_collector.track_duration("retrieve", duration)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        metrics_collector.decrement_active_operations("retrieve")


@app.put("/update/{key}")
async def update_data(key: str, request: UpdateRequest):
    """Update existing data."""
    start_time = time.time()
    metrics_collector.increment_active_operations("update")
    
    try:
        success = store.update(key, request.data, request.metadata)
        
        duration = time.time() - start_time
        metrics_collector.track_operation("update", "success" if success else "not_found")
        metrics_collector.track_duration("update", duration)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Key '{key}' not found")
        
        return {
            "success": True,
            "key": key,
            "message": "Data updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        duration = time.time() - start_time
        metrics_collector.track_operation("update", "error")
        metrics_collector.track_error("update", type(e).__name__)
        metrics_collector.track_duration("update", duration)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        metrics_collector.decrement_active_operations("update")


@app.delete("/delete/{key}")
async def delete_data(key: str):
    """Delete data by key."""
    start_time = time.time()
    metrics_collector.increment_active_operations("delete")
    
    try:
        success = store.delete(key)
        
        duration = time.time() - start_time
        metrics_collector.track_operation("delete", "success" if success else "not_found")
        metrics_collector.track_duration("delete", duration)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Key '{key}' not found")
        
        return {
            "success": True,
            "key": key,
            "message": "Data deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        duration = time.time() - start_time
        metrics_collector.track_operation("delete", "error")
        metrics_collector.track_error("delete", type(e).__name__)
        metrics_collector.track_duration("delete", duration)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        metrics_collector.decrement_active_operations("delete")


@app.get("/exists/{key}")
async def check_exists(key: str):
    """Check if key exists."""
    start_time = time.time()
    
    try:
        exists = store.exists(key)
        
        duration = time.time() - start_time
        metrics_collector.track_operation("exists", "success")
        metrics_collector.track_duration("exists", duration)
        
        return {
            "key": key,
            "exists": exists
        }
    except Exception as e:
        duration = time.time() - start_time
        metrics_collector.track_operation("exists", "error")
        metrics_collector.track_error("exists", type(e).__name__)
        metrics_collector.track_duration("exists", duration)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
async def query_data(request: QueryRequest):
    """Query data by filters."""
    start_time = time.time()
    metrics_collector.increment_active_operations("query")
    
    try:
        result = store.query(
            filters=request.filters,
            limit=request.limit,
            sort=request.sort,
            offset=request.offset
        )
        
        duration = time.time() - start_time
        metrics_collector.track_operation("query", "success")
        metrics_collector.track_duration("query", duration)
        
        return {
            "success": True,
            "items": [item.dict() for item in result.items],
            "total": result.total,
            "limit": result.limit,
            "offset": result.offset
        }
    except Exception as e:
        duration = time.time() - start_time
        metrics_collector.track_operation("query", "error")
        metrics_collector.track_error("query", type(e).__name__)
        metrics_collector.track_duration("query", duration)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        metrics_collector.decrement_active_operations("query")


@app.post("/bulk_store")
async def bulk_store_data(request: BulkStoreRequest):
    """Store multiple items at once."""
    start_time = time.time()
    metrics_collector.increment_active_operations("bulk_store")
    
    try:
        result = store.bulk_store(request.items)
        
        duration = time.time() - start_time
        metrics_collector.track_operation("bulk_store", "success" if result.success else "error")
        metrics_collector.track_duration("bulk_store", duration)
        
        return {
            "success": result.success,
            "records_loaded": result.records_loaded,
            "errors": result.errors,
            "keys": result.keys
        }
    except Exception as e:
        duration = time.time() - start_time
        metrics_collector.track_operation("bulk_store", "error")
        metrics_collector.track_error("bulk_store", type(e).__name__)
        metrics_collector.track_duration("bulk_store", duration)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        metrics_collector.decrement_active_operations("bulk_store")


@app.post("/admin/seed-companies")
async def seed_companies(request: SeedCompaniesRequest):
    """
    Admin endpoint to seed fake companies into a specific collection.
    
    Generates fake company data and stores it in the specified MongoDB collection.
    Can be called multiple times to add more companies.
    
    Args:
        request: SeedCompaniesRequest with count and collection name
        
    Returns:
        Result with number of companies stored
    """
    start_time = time.time()
    metrics_collector.increment_active_operations("seed_companies")
    
    try:
        # Generate fake companies
        companies = generate_batch(request.count)
        
        # Create a store instance for the specified collection
        collection_store = create_store(
            config.backend,
            **{**config.config, "collection": request.collection}
        )
        
        # Prepare items for bulk_store
        items = [
            {
                "key": company["key"],
                "data": company["data"],
                "metadata": company["metadata"]
            }
            for company in companies
        ]
        
        # Bulk store
        result = collection_store.bulk_store(items)
        
        duration = time.time() - start_time
        metrics_collector.track_operation("seed_companies", "success" if result.success else "error")
        metrics_collector.track_duration("seed_companies", duration)
        
        # Get total count in collection
        total_count = collection_store.count({})
        
        return {
            "success": result.success,
            "records_loaded": result.records_loaded,
            "total_in_collection": total_count,
            "collection": request.collection,
            "errors": result.errors,
            "keys": result.keys[:10]  # Return first 10 keys as sample
        }
        
    except Exception as e:
        duration = time.time() - start_time
        metrics_collector.track_operation("seed_companies", "error")
        metrics_collector.track_error("seed_companies", type(e).__name__)
        metrics_collector.track_duration("seed_companies", duration)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        metrics_collector.decrement_active_operations("seed_companies")


@app.post("/count")
async def count_data(filters: Dict[str, Any]):
    """Count items matching filters."""
    start_time = time.time()
    
    try:
        count = store.count(filters)
        
        duration = time.time() - start_time
        metrics_collector.track_operation("count", "success")
        metrics_collector.track_duration("count", duration)
        
        return {
            "count": count,
            "filters": filters
        }
    except Exception as e:
        duration = time.time() - start_time
        metrics_collector.track_operation("count", "error")
        metrics_collector.track_error("count", type(e).__name__)
        metrics_collector.track_duration("count", duration)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/distinct/{field}")
async def distinct_values(field: str, filters: Optional[Dict[str, Any]] = None):
    """Get distinct values for a field."""
    start_time = time.time()
    
    try:
        values = store.distinct(field, filters)
        
        duration = time.time() - start_time
        metrics_collector.track_operation("distinct", "success")
        metrics_collector.track_duration("distinct", duration)
        
        return {
            "field": field,
            "values": values,
            "count": len(values)
        }
    except Exception as e:
        duration = time.time() - start_time
        metrics_collector.track_operation("distinct", "error")
        metrics_collector.track_error("distinct", type(e).__name__)
        metrics_collector.track_duration("distinct", duration)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Prometheus metrics endpoint."""
    if not PROMETHEUS_AVAILABLE:
        return "# Prometheus client not available\n", 503
    
    return generate_latest()


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8007"))
    uvicorn.run(app, host="0.0.0.0", port=port)

