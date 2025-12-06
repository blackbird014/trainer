# Model Trainer

A Python module for preparing training datasets, training models, and versioning checkpoints with support for multiple frameworks.

## Features

- **Dataset Preparation**: Convert prompts and outputs to training format
- **Framework Integration**: Support for HuggingFace Transformers and PyTorch
- **Model Versioning**: Version control for model checkpoints
- **Metrics Tracking**: Track training metrics and experiments
- **Evaluation**: Evaluate model performance
- **Prometheus Metrics**: Built-in metrics for monitoring

## Installation

### Basic Installation

```bash
pip install -e .
```

### With Framework Dependencies

```bash
# HuggingFace support
pip install -e ".[huggingface]"

# PyTorch support
pip install -e ".[pytorch]"

# Experiment tracking
pip install -e ".[tracking]"

# All dependencies
pip install -e ".[all]"
```

## Quick Start

### Prepare Dataset

```python
from model_trainer import ModelTrainer

trainer = ModelTrainer()
prompts = ["Prompt 1", "Prompt 2"]
outputs = ["Output 1", "Output 2"]

examples = trainer.prepare_dataset(prompts, outputs)
```

### Save Dataset

```python
trainer.dataset_prep.save_dataset(examples, "dataset.json", format="json")
```

### Version Checkpoint

```python
version = trainer.versioner.version_checkpoint(
    checkpoint_path="model.pt",
    framework="huggingface",
    metadata={"epochs": 3, "loss": 0.5}
)
```

### Train Model

```python
from model_trainer import TrainingConfig

config = TrainingConfig(
    framework="huggingface",
    model_name="gpt2",
    epochs=3,
    batch_size=8,
    learning_rate=5e-5
)

checkpoint = trainer.train(examples, config)
print(f"Trained model version: {checkpoint.version}")
```

## API Service

The module includes a FastAPI service for exposing training functionality via REST API:

```bash
cd _dev/model-trainer
python api_service.py
```

The service runs on port 8005 (configurable via `PORT` environment variable) and provides:

- `GET /` - API information
- `GET /health` - Health check
- `POST /prepare_dataset` - Prepare training dataset
- `POST /train` - Train a model
- `POST /evaluate` - Evaluate a model
- `GET /versions/{framework}` - List model versions
- `GET /metrics` - Prometheus metrics endpoint

### Example API Usage

```bash
# Prepare dataset
curl -X POST http://localhost:8005/prepare_dataset \
  -H "Content-Type: application/json" \
  -d '{
    "prompts": ["Prompt 1", "Prompt 2"],
    "outputs": ["Output 1", "Output 2"]
  }'

# Train model
curl -X POST http://localhost:8005/train \
  -H "Content-Type: application/json" \
  -d '{
    "examples": [
      {"prompt": "P1", "output": "O1"},
      {"prompt": "P2", "output": "O2"}
    ],
    "framework": "huggingface",
    "epochs": 3
  }'
```

## Prometheus Metrics

The module exposes Prometheus metrics at `/metrics` endpoint:

- `model_trainer_training_runs_total` - Total training runs (by framework, status)
- `model_trainer_training_duration_seconds` - Training duration histogram
- `model_trainer_dataset_size` - Dataset size histogram
- `model_trainer_evaluation_runs_total` - Total evaluations (by model_version, status)
- `model_trainer_model_versions_total` - Total model versions (by framework)
- `model_trainer_checkpoint_size_bytes` - Checkpoint size histogram
- `model_trainer_errors_total` - Total errors (by error_type, framework)
- `model_trainer_active_training_runs` - Active training runs gauge

### Monitoring Setup

1. **Start the API service**:
   ```bash
   cd _dev/model-trainer
   python api_service.py
   ```

2. **Configure Prometheus** (already configured in centralized monitoring):
   The centralized monitoring at `_dev/monitoring/` is already configured to scrape model-trainer on port 8005.

3. **View Grafana Dashboard**:
   - Start centralized monitoring: `cd _dev/monitoring && docker-compose up -d`
   - Access Grafana: http://localhost:3000
   - Navigate to "Model Trainer Dashboard"

## API Reference

### ModelTrainer

Main trainer class.

```python
trainer = ModelTrainer(
    checkpoint_dir="checkpoints",
    enable_metrics=True
)

# Prepare dataset
examples = trainer.prepare_dataset(prompts, outputs)

# Train model
checkpoint = trainer.train(examples, config)

# Evaluate model
metrics = trainer.evaluate(model, test_set)
```

### TrainingConfig

Training configuration.

```python
config = TrainingConfig(
    framework="huggingface",  # or "pytorch"
    model_name="gpt2",
    epochs=3,
    batch_size=8,
    learning_rate=5e-5,
    hyperparameters={"warmup_steps": 100}
)
```

### DatasetPreparator

Dataset preparation utilities.

```python
preparator = DatasetPreparator()

# Prepare from prompts/outputs
examples = preparator.prepare_dataset(prompts, outputs)

# Save dataset
preparator.save_dataset(examples, "dataset.json", format="json")

# Load dataset
examples = preparator.load_dataset("dataset.json", format="json")
```

### ModelVersioner

Model checkpoint versioning.

```python
versioner = ModelVersioner(checkpoint_dir="checkpoints")

# Version checkpoint
version = versioner.version_checkpoint(
    checkpoint_path="model.pt",
    framework="huggingface",
    metadata={"epochs": 3}
)

# List versions
versions = versioner.list_versions("huggingface")

# Get checkpoint info
info = versioner.get_checkpoint_info("huggingface", version)
```

## Supported Frameworks

### HuggingFace Transformers

```python
config = TrainingConfig(
    framework="huggingface",
    model_name="gpt2",
    epochs=3
)
checkpoint = trainer.train(examples, config)
```

### PyTorch

```python
config = TrainingConfig(
    framework="pytorch",
    epochs=3
)
checkpoint = trainer.train(examples, config)
```

## Development

### Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in development mode
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

Or use the test runner:

```bash
./run_tests.sh
```

## Package Structure

```
model-trainer/
├── src/
│   ├── model_trainer/
│   │   ├── __init__.py
│   │   ├── trainer.py              # Main trainer class
│   │   ├── dataset_prep.py         # Dataset preparation
│   │   ├── versioning.py           # Model versioning
│   │   ├── metrics.py               # Prometheus metrics
│   │   └── integrations/
│   │       ├── huggingface_integration.py
│   │       └── pytorch_integration.py
│   └── tests/
├── examples/
│   ├── basic_usage.py
│   └── integration_example.py
├── api_service.py                  # FastAPI service
├── pyproject.toml
└── README.md
```

## Dependencies

### Core Dependencies
- `prometheus-client>=0.19.0` - Metrics collection
- `fastapi>=0.104.0` - API framework
- `uvicorn[standard]>=0.24.0` - ASGI server

### Optional Dependencies
- `transformers>=4.30.0` - HuggingFace Transformers
- `datasets>=2.12.0` - HuggingFace Datasets
- `torch>=2.0.0` - PyTorch
- `wandb>=0.15.0` - Weights & Biases tracking
- `mlflow>=2.5.0` - MLflow tracking

## Examples

See `examples/` directory for:
- Basic usage examples
- Integration examples with other modules

## License

MIT

