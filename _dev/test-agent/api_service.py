"""
FastAPI service for test-agent module.

Exposes test execution and analysis functionality via REST API.
Run on port 8006 (configurable).
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

from test_agent import TestAgent

# Initialize FastAPI app
app = FastAPI(
    title="Test Agent API",
    description="Microservice for test execution and analysis",
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

# Initialize test agent
agent = TestAgent(enable_metrics=True)


# Request/Response models
class RunTestsRequest(BaseModel):
    module: Optional[str] = None
    test_path: Optional[str] = None
    coverage: bool = False
    verbose: bool = True


class GenerateTestsRequest(BaseModel):
    module_path: str
    strategy: str = "comprehensive"  # "comprehensive", "minimal", "smart", "missing"
    output_dir: Optional[str] = None


class GenerateMissingTestsRequest(BaseModel):
    module: str
    output_dir: Optional[str] = None


class GenerateIntegrationTestsRequest(BaseModel):
    modules: List[str]
    output_dir: Optional[str] = None


class GenerateContractTestsRequest(BaseModel):
    consumer_module: str
    provider_module: str
    output_dir: Optional[str] = None


class AnalyzeDependenciesRequest(BaseModel):
    module: str


class IntegrationTestRequest(BaseModel):
    modules: List[str]


# Routes
@app.get("/")
async def root():
    """API information."""
    return {
        "name": "Test Agent API",
        "version": "0.1.0",
        "endpoints": {
            "discover_modules": "/discover_modules",
            "discover_tests": "/discover_tests",
            "run_tests": "/run_tests",
            "run_integration_tests": "/run_integration_tests",
            "check_coverage": "/check_coverage",
            "generate_tests": "/generate_tests",
            "find_missing_tests": "/find_missing_tests",
            "generate_missing_tests": "/generate_missing_tests",
            "generate_integration_tests": "/generate_integration_tests",
            "generate_contract_tests": "/generate_contract_tests",
            "analyze_dependencies": "/analyze_dependencies",
            "metrics": "/metrics",
            "health": "/health",
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "test-agent"}


@app.get("/discover_modules")
async def discover_modules():
    """Discover all modules in the project."""
    try:
        modules = agent.discover_modules()
        return {
            "success": True,
            "modules": modules,
            "count": len(modules)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/discover_tests")
async def discover_tests(module: Optional[str] = None):
    """Discover test files in modules."""
    try:
        tests = agent.discover_tests(module=module)
        return {
            "success": True,
            "tests": tests,
            "module": module or "all"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run_tests")
async def run_tests(request: RunTestsRequest):
    """Run tests for a module or specific test path."""
    try:
        results = agent.run_tests(
            module=request.module,
            test_path=request.test_path,
            coverage=request.coverage,
            verbose=request.verbose
        )
        return {
            "success": True,
            "results": {
                "passed": results.passed,
                "failed": results.failed,
                "skipped": results.skipped,
                "errors": results.errors,
                "duration": results.duration,
                "module": results.module
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run_integration_tests")
async def run_integration_tests(request: IntegrationTestRequest):
    """Run integration tests across multiple modules."""
    try:
        results = agent.run_integration_tests(request.modules)
        return {
            "success": True,
            "results": {
                "passed": results.passed,
                "failed": results.failed,
                "skipped": results.skipped,
                "errors": results.errors,
                "duration": results.duration,
                "modules": request.modules
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/check_coverage")
async def check_coverage(module: Optional[str] = None, threshold: Optional[float] = None):
    """Check test coverage for a module."""
    try:
        coverage = agent.check_coverage(module=module, threshold=threshold)
        return {
            "success": True,
            "coverage": {
                "percentage": coverage.percentage,
                "lines_covered": coverage.lines_covered,
                "lines_total": coverage.lines_total,
                "branches_covered": coverage.branches_covered,
                "branches_total": coverage.branches_total,
                "module_breakdown": coverage.module_breakdown,
                "module": coverage.module
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate_tests")
async def generate_tests(request: GenerateTestsRequest):
    """Generate tests for a module (opt-in, explicit)."""
    try:
        tests = agent.generate_tests(
            module_path=request.module_path,
            strategy=request.strategy,
            output_dir=request.output_dir
        )
        return {
            "success": True,
            "tests_generated": len(tests),
            "strategy": request.strategy,
            "tests": [
                {
                    "name": test.name,
                    "module": test.module,
                    "target": test.target,
                    "test_type": test.test_type
                }
                for test in tests
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/find_missing_tests")
async def find_missing_tests(module: str):
    """Find functions/classes that lack test coverage."""
    try:
        missing = agent.find_missing_tests(module)
        total_missing = sum(len(items) for items in missing.values())
        return {
            "success": True,
            "module": module,
            "missing_tests": missing,
            "total_missing": total_missing,
            "files_with_missing": len(missing)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate_missing_tests")
async def generate_missing_tests(request: GenerateMissingTestsRequest):
    """Generate tests only for missing coverage."""
    try:
        tests = agent.generate_missing_tests(
            module=request.module,
            output_dir=request.output_dir
        )
        return {
            "success": True,
            "tests_generated": len(tests),
            "module": request.module,
            "tests": [
                {
                    "name": test.name,
                    "module": test.module,
                    "target": test.target,
                    "test_type": test.test_type
                }
                for test in tests
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate_integration_tests")
async def generate_integration_tests(request: GenerateIntegrationTestsRequest):
    """Generate integration tests for module interactions."""
    try:
        tests = agent.generate_integration_tests(
            modules=request.modules,
            output_dir=request.output_dir
        )
        return {
            "success": True,
            "tests_generated": len(tests),
            "modules": request.modules,
            "tests": [
                {
                    "name": test.name,
                    "module": test.module,
                    "target": test.target,
                    "test_type": test.test_type
                }
                for test in tests
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate_contract_tests")
async def generate_contract_tests(request: GenerateContractTestsRequest):
    """Generate contract tests between modules."""
    try:
        tests = agent.generate_contract_tests(
            consumer_module=request.consumer_module,
            provider_module=request.provider_module,
            output_dir=request.output_dir
        )
        return {
            "success": True,
            "tests_generated": len(tests),
            "consumer": request.consumer_module,
            "provider": request.provider_module,
            "tests": [
                {
                    "name": test.name,
                    "module": test.module,
                    "target": test.target,
                    "test_type": test.test_type
                }
                for test in tests
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analyze_dependencies")
async def analyze_dependencies(module: str):
    """Analyze module dependencies."""
    try:
        deps = agent.analyze_dependencies(module)
        return {
            "success": True,
            "module": module,
            "dependencies": deps
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Prometheus metrics endpoint."""
    if not PROMETHEUS_AVAILABLE:
        return "# Prometheus client not available\n", 503

    return generate_latest()


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8006))

    print("=" * 80)
    print("Test Agent FastAPI Service")
    print("=" * 80)
    print()
    print(f"Starting server on http://0.0.0.0:{port}")
    print()
    print("Endpoints:")
    print(f"  - http://localhost:{port}/              - API info")
    print(f"  - http://localhost:{port}/docs          - Swagger UI")
    print(f"  - http://localhost:{port}/metrics       - Prometheus metrics")
    print(f"  - http://localhost:{port}/health         - Health check")
    print(f"  - http://localhost:{port}/discover_modules - Discover modules")
    print(f"  - http://localhost:{port}/discover_tests - Discover tests")
    print(f"  - http://localhost:{port}/run_tests     - Run tests")
    print(f"  - http://localhost:{port}/check_coverage - Check coverage")
    print(f"  - http://localhost:{port}/generate_tests - Generate tests")
    print()
    print("Metrics:")
    print("  - test_agent_test_runs_total")
    print("  - test_agent_test_duration_seconds")
    print("  - test_agent_tests_passed_total")
    print("  - test_agent_tests_failed_total")
    print("  - test_agent_coverage_percentage")
    print("  - test_agent_tests_generated_total")
    print()
    print("=" * 80)
    print()

    uvicorn.run(app, host="0.0.0.0", port=port)

