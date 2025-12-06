"""
FastAPI service for PromptManager microservice.

Exposes PromptManager functionality via REST API.
Run on port 8000.
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from pathlib import Path
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from prompt_manager import PromptManager, PromptTemplate, LogLevel
from prompt_manager.security_middleware import SecurityMiddleware, RateLimitMiddleware

# Try to import SecurityModule (optional dependency)
try:
    from prompt_security import SecurityModule, SecurityConfig
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False
    SecurityModule = None
    SecurityConfig = None

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Initialize FastAPI app
app = FastAPI(
    title="Prompt Manager API",
    description="Microservice for prompt management operations",
    version="0.1.0"
)

# Initialize SecurityModule (if available)
security_module = None
if SECURITY_AVAILABLE:
    # Get security configuration from environment or use defaults
    security_config = SecurityConfig(
        max_length=int(os.getenv("SECURITY_MAX_LENGTH", 1000)),
        strict_mode=os.getenv("SECURITY_STRICT_MODE", "true").lower() == "true",
        log_security_events=os.getenv("SECURITY_LOG_EVENTS", "true").lower() == "true"
    )
    security_module = SecurityModule(config=security_config)
    print("✓ Security module initialized")
else:
    print("⚠ Security module not available (prompt-security package not installed)")

# Rate limiting configuration
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT_REQUESTS_PER_MINUTE = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "60"))

# Add rate limiting middleware (before security middleware)
if RATE_LIMIT_ENABLED:
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=RATE_LIMIT_REQUESTS_PER_MINUTE,
        enabled=True
    )
    print(f"✓ Rate limiting enabled ({RATE_LIMIT_REQUESTS_PER_MINUTE} requests/minute)")

# Add security middleware (after rate limiting, before CORS)
if security_module:
    app.add_middleware(
        SecurityMiddleware,
        security_module=security_module,
        enabled=True
    )
    print("✓ Security middleware enabled")

# CORS middleware for Express integration (should be last)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Express app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize PromptManager with metrics and security
manager = PromptManager(
    context_dir=str(PROJECT_ROOT / "information" / "context"),
    cache_enabled=True,
    track_tokens=True,
    model="gpt-4",
    enable_metrics=True,
    log_level=LogLevel.INFO,
    security_module=security_module  # Pass security module to PromptManager
)


# Pydantic models for request/response
class LoadPromptRequest(BaseModel):
    prompt_path: str


class LoadContextsRequest(BaseModel):
    context_paths: List[str]


class FillTemplateRequest(BaseModel):
    template_content: str
    template_path: Optional[str] = None
    params: Dict[str, Any]


class ComposeRequest(BaseModel):
    templates: List[str]
    strategy: str = "sequential"


class PromptResponse(BaseModel):
    content: str
    length: int


class StatsResponse(BaseModel):
    token_usage: Dict[str, Any]
    operation_stats: Dict[str, Dict]


class HealthResponse(BaseModel):
    status: str
    service: str
    metrics_enabled: bool


# Routes
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Prompt Manager API",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "stats": "/stats",
            "load_prompt": "/prompt/load",
            "load_contexts": "/prompt/load-contexts",
            "fill_template": "/prompt/fill",
            "compose": "/prompt/compose"
        },
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        service="prompt-manager",
        metrics_enabled=manager.logger.metrics_enabled
    )


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Prometheus metrics endpoint."""
    return PlainTextResponse(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.get("/stats", response_model=StatsResponse)
async def stats():
    """Get current token usage and operation statistics."""
    return StatsResponse(
        token_usage=manager.get_token_usage(),
        operation_stats=manager.get_operation_stats()
    )


@app.post("/prompt/load", response_model=PromptResponse)
async def load_prompt(request: LoadPromptRequest):
    """Load a prompt template from a file."""
    try:
        template = manager.load_prompt(request.prompt_path)
        return PromptResponse(
            content=template.content,
            length=len(template.content)
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/prompt/load-contexts", response_model=PromptResponse)
async def load_contexts(request: LoadContextsRequest):
    """Load and merge multiple context files."""
    try:
        contexts = manager.load_contexts(request.context_paths)
        return PromptResponse(
            content=contexts,
            length=len(contexts)
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/prompt/fill", response_model=PromptResponse)
async def fill_template(request: FillTemplateRequest):
    """Fill a template with parameters."""
    try:
        template = PromptTemplate(
            content=request.template_content,
            path=request.template_path
        )
        filled = manager.fill_template(template, request.params)
        return PromptResponse(
            content=filled,
            length=len(filled)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Check if it's a security-related exception
        if SECURITY_AVAILABLE:
            from prompt_security import ValidationError, InjectionDetectedError
            if isinstance(e, ValidationError):
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Validation failed",
                        "message": str(e),
                        "errors": e.validation_result.errors,
                        "warnings": e.validation_result.warnings
                    }
                )
            elif isinstance(e, InjectionDetectedError):
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "Prompt injection detected",
                        "message": str(e),
                        "flags": e.detection_result.flags[:5]
                    }
                )
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/prompt/compose", response_model=PromptResponse)
async def compose_prompts(request: ComposeRequest):
    """Compose multiple prompts using a strategy."""
    try:
        templates = [PromptTemplate(content=t) for t in request.templates]
        composed = manager.compose(templates, strategy=request.strategy)
        return PromptResponse(
            content=composed,
            length=len(composed)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Check if it's a security-related exception
        if SECURITY_AVAILABLE:
            from prompt_security import ValidationError, InjectionDetectedError
            if isinstance(e, ValidationError):
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Validation failed",
                        "message": str(e),
                        "errors": e.validation_result.errors,
                        "warnings": e.validation_result.warnings
                    }
                )
            elif isinstance(e, InjectionDetectedError):
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "Prompt injection detected",
                        "message": str(e),
                        "flags": e.detection_result.flags[:5]
                    }
                )
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/prompt/test")
async def test():
    """Test endpoint to generate some metrics."""
    try:
        # Load contexts
        contexts = manager.load_contexts([
            "biotech/01-introduction.md",
            "biotech/molecular-biology-foundations.md"
        ])
        
        # Fill template
        template = PromptTemplate("Test template with {VAR}")
        filled = manager.fill_template(template, {"VAR": "test_value"})
        
        # Compose
        composed = manager.compose([
            PromptTemplate("Prompt 1"),
            PromptTemplate("Prompt 2")
        ])
        
        return {
            "status": "success",
            "message": "Test operations completed",
            "contexts_size": len(contexts),
            "filled_size": len(filled),
            "composed_size": len(composed)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 80)
    print("Prompt Manager FastAPI Service")
    print("=" * 80)
    print()
    print("Starting server on http://0.0.0.0:8000")
    print()
    print("Security Features:")
    if security_module:
        print(f"  ✓ Security module: Enabled (strict_mode={security_module.config.strict_mode})")
    else:
        print("  ⚠ Security module: Not available")
    if RATE_LIMIT_ENABLED:
        print(f"  ✓ Rate limiting: Enabled ({RATE_LIMIT_REQUESTS_PER_MINUTE} req/min)")
    else:
        print("  ⚠ Rate limiting: Disabled")
    print()
    print("Endpoints:")
    print("  - http://localhost:8000/              - API info")
    print("  - http://localhost:8000/docs          - Swagger UI")
    print("  - http://localhost:8000/metrics       - Prometheus metrics")
    print("  - http://localhost:8000/health         - Health check")
    print("  - http://localhost:8000/stats          - Token stats")
    print("  - http://localhost:8000/prompt/load    - Load prompt")
    print("  - http://localhost:8000/prompt/fill    - Fill template")
    print("  - http://localhost:8000/prompt/compose - Compose prompts")
    print()
    print("Security Metrics:")
    print("  - prompt_manager_security_validation_total")
    print("  - prompt_manager_security_injection_detected_total")
    print("  - prompt_manager_security_validation_duration_seconds")
    print("  - prompt_manager_security_rate_limit_hits_total")
    print()
    print("Next steps:")
    print("  1. Keep this server running")
    print("  2. Start Express app: npm start (in express-app directory)")
    print("  3. View Grafana: http://localhost:3001 (if configured)")
    print("  4. View Prometheus: http://localhost:9090")
    print()
    print("=" * 80)
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

