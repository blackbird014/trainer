"""
FastAPI service for model-trainer module.

Exposes model training functionality via REST API and Prometheus metrics.
Run on port 8005 (configurable).
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

try:
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

from model_trainer import ModelTrainer, TrainingConfig, TrainingExample

# Initialize FastAPI app
app = FastAPI(
    title="Model Trainer API",
    description="Microservice for model training operations",
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

# Initialize trainer
trainer = ModelTrainer(enable_metrics=True)


# Request/Response models
class PrepareDatasetRequest(BaseModel):
    prompts: List[str]
    outputs: List[str]
    dataset_type: str = "prompt_output"


class TrainingRequest(BaseModel):
    examples: List[Dict[str, str]]  # [{"prompt": "...", "output": "..."}]
    framework: str = "huggingface"
    model_name: Optional[str] = None
    epochs: int = 3
    batch_size: int = 8
    learning_rate: float = 5e-5
    hyperparameters: Optional[Dict[str, Any]] = None


class EvaluationRequest(BaseModel):
    model_path: str
    test_examples: List[Dict[str, str]]
    model_version: Optional[str] = None


# Routes
@app.get("/")
async def root():
    """API information."""
    return {
        "name": "Model Trainer API",
        "version": "0.1.0",
        "endpoints": {
            "prepare_dataset": "/prepare_dataset",
            "train": "/train",
            "evaluate": "/evaluate",
            "list_versions": "/versions/{framework}",
            "metrics": "/metrics",
            "health": "/health",
        },
        "supported_frameworks": ["huggingface", "pytorch"]
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "model-trainer"}


@app.post("/prepare_dataset")
async def prepare_dataset(request: PrepareDatasetRequest):
    """Prepare training dataset from prompts and outputs."""
    try:
        examples = trainer.prepare_dataset(
            prompts=request.prompts,
            outputs=request.outputs,
            dataset_type=request.dataset_type
        )
        return {
            "success": True,
            "dataset_size": len(examples),
            "examples": [
                {"prompt": ex.prompt, "output": ex.output}
                for ex in examples
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/train")
async def train(request: TrainingRequest):
    """Train a model."""
    try:
        # Convert examples
        examples = [
            TrainingExample(prompt=ex["prompt"], output=ex["output"])
            for ex in request.examples
        ]

        # Create config
        config = TrainingConfig(
            framework=request.framework,
            model_name=request.model_name,
            epochs=request.epochs,
            batch_size=request.batch_size,
            learning_rate=request.learning_rate,
            hyperparameters=request.hyperparameters
        )

        # Train
        checkpoint = trainer.train(examples, config)

        return {
            "success": True,
            "checkpoint": {
                "path": checkpoint.path,
                "version": checkpoint.version,
                "framework": checkpoint.framework,
                "metrics": checkpoint.metrics
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evaluate")
async def evaluate(request: EvaluationRequest):
    """Evaluate a model."""
    try:
        # Convert examples
        test_examples = [
            TrainingExample(prompt=ex["prompt"], output=ex["output"])
            for ex in request.test_examples
        ]

        # Placeholder: load model and evaluate
        # In real implementation, would load model from request.model_path
        metrics = trainer.evaluate(
            model=None,  # Would load actual model
            test_set=test_examples,
            model_version=request.model_version
        )

        return {
            "success": True,
            "metrics": metrics,
            "model_version": request.model_version
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/versions/{framework}")
async def list_versions(framework: str):
    """List all model versions for a framework."""
    try:
        versions = trainer.versioner.list_versions(framework)
        return {
            "framework": framework,
            "versions": versions,
            "count": len(versions)
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

    port = int(os.getenv("PORT", 8005))

    print("=" * 80)
    print("Model Trainer FastAPI Service")
    print("=" * 80)
    print()
    print(f"Starting server on http://0.0.0.0:{port}")
    print()
    print("Endpoints:")
    print(f"  - http://localhost:{port}/              - API info")
    print(f"  - http://localhost:{port}/docs          - Swagger UI")
    print(f"  - http://localhost:{port}/metrics       - Prometheus metrics")
    print(f"  - http://localhost:{port}/health         - Health check")
    print(f"  - http://localhost:{port}/prepare_dataset - Prepare dataset")
    print(f"  - http://localhost:{port}/train          - Train model")
    print(f"  - http://localhost:{port}/evaluate       - Evaluate model")
    print(f"  - http://localhost:{port}/versions/{{framework}} - List versions")
    print()
    print("Supported Frameworks:")
    print("  - huggingface")
    print("  - pytorch")
    print()
    print("Metrics:")
    print("  - model_trainer_training_runs_total")
    print("  - model_trainer_training_duration_seconds")
    print("  - model_trainer_dataset_size")
    print("  - model_trainer_evaluation_runs_total")
    print("  - model_trainer_model_versions_total")
    print("  - model_trainer_checkpoint_size_bytes")
    print("  - model_trainer_errors_total")
    print("  - model_trainer_active_training_runs")
    print()
    print("=" * 80)
    print()

    uvicorn.run(app, host="0.0.0.0", port=port)

