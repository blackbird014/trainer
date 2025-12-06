"""
Model Training Integration Module

Provides functionality for:
- Preparing training data from prompts and outputs
- Integrating with training frameworks (HuggingFace, PyTorch, etc.)
- Tracking training metrics
- Versioning model checkpoints
- Evaluating model performance
"""

from model_trainer.trainer import ModelTrainer
from model_trainer.dataset_prep import DatasetPreparator
from model_trainer.metrics import MetricsCollector
from model_trainer.versioning import ModelVersioner

__all__ = [
    "ModelTrainer",
    "DatasetPreparator",
    "MetricsCollector",
    "ModelVersioner",
]

__version__ = "0.1.0"

