"""
FastAPI service for format-converter module.

Exposes format conversion functionality via REST API and Prometheus metrics.
Run on port 8004 (configurable).
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Union, Dict, Any, Optional

try:
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

from format_converter import FormatConverter

# Initialize FastAPI app
app = FastAPI(
    title="Format Converter API",
    description="Microservice for format conversion operations",
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

# Initialize converter
css_path = os.getenv("CSS_PATH", "../../output/css/report.css")
converter = FormatConverter(enable_metrics=True, css_path=css_path if os.path.exists(css_path) else None)


# Request/Response models
class ConvertRequest(BaseModel):
    content: Union[str, Dict[str, Any]]
    source_format: str = "auto"
    target_format: str = "html"
    options: Optional[Dict[str, Any]] = None


class ConvertResponse(BaseModel):
    success: bool
    content: Optional[Union[str, Dict[str, Any]]] = None
    source_format: str
    target_format: str
    error: Optional[str] = None


# Routes
@app.get("/")
async def root():
    """API information."""
    return {
        "name": "Format Converter API",
        "version": "0.1.0",
        "endpoints": {
            "convert": "/convert",
            "metrics": "/metrics",
            "health": "/health",
            "detect": "/detect",
        },
        "supported_formats": {
            "source": ["auto", "markdown", "json", "text"],
            "target": ["html", "pdf", "markdown", "json"],
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "format-converter"}


@app.post("/detect")
async def detect_format(request: Dict[str, Any]):
    """Detect format of content."""
    content = request.get("content")
    if content is None:
        raise HTTPException(status_code=400, detail="Missing 'content' field")

    detected = converter.detect_format(content)
    return {
        "format": detected,
        "content_type": type(content).__name__
    }


@app.post("/convert", response_model=ConvertResponse)
async def convert(request: ConvertRequest):
    """Convert content from source format to target format."""
    try:
        options = request.options or {}
        result = converter.convert(
            source=request.content,
            source_format=request.source_format,
            target_format=request.target_format,
            **options
        )

        # Handle PDF (bytes) response
        if request.target_format == "pdf":
            return Response(
                content=result,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f'attachment; filename="output.pdf"'
                }
            )

        return ConvertResponse(
            success=True,
            content=result if isinstance(result, str) else result.decode('utf-8') if isinstance(result, bytes) else str(result),
            source_format=request.source_format,
            target_format=request.target_format,
        )

    except Exception as e:
        return ConvertResponse(
            success=False,
            source_format=request.source_format,
            target_format=request.target_format,
            error=str(e),
        )


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Prometheus metrics endpoint."""
    if not PROMETHEUS_AVAILABLE:
        return "# Prometheus client not available\n", 503

    return generate_latest()


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8004))

    print("=" * 80)
    print("Format Converter FastAPI Service")
    print("=" * 80)
    print()
    print(f"Starting server on http://0.0.0.0:{port}")
    print()
    print("Endpoints:")
    print(f"  - http://localhost:{port}/              - API info")
    print(f"  - http://localhost:{port}/docs          - Swagger UI")
    print(f"  - http://localhost:{port}/metrics       - Prometheus metrics")
    print(f"  - http://localhost:{port}/health         - Health check")
    print(f"  - http://localhost:{port}/detect         - Detect format")
    print(f"  - http://localhost:{port}/convert       - Convert format")
    print()
    print("Supported Conversions:")
    print("  - markdown → html, pdf, json")
    print("  - json → markdown, html, pdf")
    print("  - html → pdf")
    print("  - auto-detection supported")
    print()
    print("Metrics:")
    print("  - format_converter_operations_total")
    print("  - format_converter_operation_duration_seconds")
    print("  - format_converter_data_size_bytes")
    print("  - format_converter_errors_total")
    print("  - format_converter_auto_detections_total")
    print()
    print("=" * 80)
    print()

    uvicorn.run(app, host="0.0.0.0", port=port)

