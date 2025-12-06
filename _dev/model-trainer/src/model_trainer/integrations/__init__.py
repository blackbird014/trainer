"""Framework integrations."""

from model_trainer.integrations.huggingface_integration import HuggingFaceIntegration
from model_trainer.integrations.pytorch_integration import PyTorchIntegration

__all__ = [
    "HuggingFaceIntegration",
    "PyTorchIntegration",
]

