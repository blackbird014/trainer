#!/usr/bin/env python3
"""
Web Dashboard for Trainer Project Modules

Provides a centralized web interface for:
- Test analysis and coverage reports
- Module navigation and links
- Data store browser
- Format converter HTML viewer
- Statistics and monitoring links

Usage:
    python tools/dashboard.py

Or:
    cd _dev/test-agent
    python tools/dashboard.py
"""

import sys
from pathlib import Path
import json
from datetime import datetime
from typing import Optional, Dict, Any, List

# Add test-agent to path
script_dir = Path(__file__).parent
test_agent_dir = script_dir.parent
test_agent_src = test_agent_dir / "src"
sys.path.insert(0, str(test_agent_src))

try:
    from fastapi import FastAPI, Request, HTTPException
    from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
    from fastapi.staticfiles import StaticFiles
    from jinja2 import Environment, FileSystemLoader
    import uvicorn
except ImportError:
    print("Error: FastAPI and uvicorn are required for the dashboard.")
    print("Install with: pip install fastapi uvicorn jinja2")
    sys.exit(1)

from test_agent import TestAgent

# Setup paths
PROJECT_ROOT = test_agent_dir.parent.parent
REPORTS_DIR = test_agent_dir / "reports" / "coverage-reports"
TEMPLATES_DIR = test_agent_dir / "tools" / "templates"
STATIC_DIR = test_agent_dir / "tools" / "static"

# Create directories
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Initialize FastAPI
app = FastAPI(title="Trainer Project Dashboard", version="1.0.0")

# Initialize Jinja2 templates
jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

def render_template(template_name: str, context: dict) -> str:
    """Render a Jinja2 template."""
    template = jinja_env.get_template(template_name)
    return template.render(**context)

# Initialize test agent
test_agent = TestAgent(project_root=str(PROJECT_ROOT))

# Module API ports (if services are running)
MODULE_PORTS = {
    "test-agent": 8006,
    "data-store": 8007,
    "format-converter": 8004,
    "data-retriever": 8003,
    "prompt-manager": 8001,
    "llm-provider": 8002,
    "model-trainer": 8005,
}

# Grafana and Prometheus
MONITORING = {
    "grafana": "http://localhost:3000",
    "prometheus": "http://localhost:9090",
}


@app.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Main dashboard page."""
    modules = test_agent.discover_modules()
    
    # Check which modules have API services running
    module_status = {}
    for module in modules:
        port = MODULE_PORTS.get(module)
        if port:
            # Could check if service is running (optional)
            module_status[module] = {
                "port": port,
                "url": f"http://localhost:{port}",
                "running": True  # Assume running, could check with requests
            }
    
    # Get latest test analysis summary
    summary_file = REPORTS_DIR / "overall_summary.json"
    test_summary = None
    if summary_file.exists():
        try:
            with open(summary_file) as f:
                test_summary = json.load(f)
        except Exception:
            pass
    
    html = render_template("dashboard.html", {
        "modules": modules,
        "module_status": module_status,
        "monitoring": MONITORING,
        "test_summary": test_summary,
        "reports_dir": str(REPORTS_DIR.relative_to(PROJECT_ROOT)),
    })
    return HTMLResponse(content=html)


@app.get("/test-analysis", response_class=HTMLResponse)
async def test_analysis(request: Request, module: Optional[str] = None):
    """Test analysis viewer."""
    summary_file = REPORTS_DIR / "overall_summary.json"
    
    if not summary_file.exists():
        html = render_template("error.html", {
            "error": "No test analysis reports found. Run comprehensive_analysis.py first.",
            "title": "Test Analysis"
        })
        return HTMLResponse(content=html)
    
    with open(summary_file) as f:
        data = json.load(f)
    
    if module:
        # Show specific module
        module_data = data.get("modules", {}).get(module)
        if not module_data:
            raise HTTPException(status_code=404, detail=f"Module {module} not found")
        
        html = render_template("module_analysis.html", {
            "module": module,
            "data": module_data,
            "all_modules": list(data.get("modules", {}).keys()),
        })
        return HTMLResponse(content=html)
    else:
        # Show overall summary
        html = render_template("test_analysis.html", {
            "summary": data,
            "modules": list(data.get("modules", {}).keys()),
        })
        return HTMLResponse(content=html)


@app.get("/api/test-analysis")
async def api_test_analysis(module: Optional[str] = None):
    """API endpoint for test analysis data."""
    summary_file = REPORTS_DIR / "overall_summary.json"
    
    if not summary_file.exists():
        return JSONResponse({"error": "No reports found"}, status_code=404)
    
    with open(summary_file) as f:
        data = json.load(f)
    
    if module:
        module_data = data.get("modules", {}).get(module)
        if not module_data:
            raise HTTPException(status_code=404, detail=f"Module {module} not found")
        return JSONResponse(module_data)
    
    return JSONResponse(data)


@app.get("/data-store", response_class=HTMLResponse)
async def data_store_browser(request: Request):
    """Data store browser page."""
    html = render_template("data_store.html", {
        "api_url": f"http://localhost:{MODULE_PORTS.get('data-store', 8007)}",
    })
    return HTMLResponse(content=html)


@app.get("/format-converter", response_class=HTMLResponse)
async def format_converter_viewer(request: Request):
    """Format converter HTML viewer."""
    # Link to the existing HTML viewer (from format-converter examples)
    viewer_url = f"http://localhost:8888"  # format-converter HTML viewer port
    
    html = render_template("format_converter.html", {
        "viewer_url": viewer_url,
        "api_url": f"http://localhost:{MODULE_PORTS.get('format-converter', 8004)}",
    })
    return HTMLResponse(content=html)


@app.get("/modules", response_class=HTMLResponse)
async def modules_page(request: Request):
    """Module navigation and links page."""
    modules = test_agent.discover_modules()
    
    module_info = []
    for module in modules:
        port = MODULE_PORTS.get(module)
        info = {
            "name": module,
            "port": port,
            "api_url": f"http://localhost:{port}" if port else None,
            "has_tests": len(test_agent.discover_tests(module).get(module, [])) > 0,
        }
        module_info.append(info)
    
    html = render_template("modules.html", {
        "modules": module_info,
        "monitoring": MONITORING,
    })
    return HTMLResponse(content=html)


@app.get("/api/modules")
async def api_modules():
    """API endpoint for module information."""
    modules = test_agent.discover_modules()
    
    module_info = []
    for module in modules:
        tests = test_agent.discover_tests(module)
        port = MODULE_PORTS.get(module)
        
        info = {
            "name": module,
            "port": port,
            "api_url": f"http://localhost:{port}" if port else None,
            "test_count": len(tests.get(module, [])),
        }
        module_info.append(info)
    
    return JSONResponse({"modules": module_info})


@app.get("/health")
async def health():
    """Health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "modules_discovered": len(test_agent.discover_modules()),
    })


def main():
    """Run the dashboard server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Trainer Project Dashboard")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8889, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("Trainer Project Dashboard")
    print("=" * 80)
    print(f"\nStarting server on http://{args.host}:{args.port}")
    print(f"\nAvailable pages:")
    print(f"  - Main Dashboard: http://{args.host}:{args.port}/")
    print(f"  - Test Analysis: http://{args.host}:{args.port}/test-analysis")
    print(f"  - Data Store: http://{args.host}:{args.port}/data-store")
    print(f"  - Format Converter: http://{args.host}:{args.port}/format-converter")
    print(f"  - Modules: http://{args.host}:{args.port}/modules")
    print(f"\nPress Ctrl+C to stop\n")
    print("=" * 80)
    
    uvicorn.run(app, host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()

