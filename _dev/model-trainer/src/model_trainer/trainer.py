"""
Main model trainer class.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import time

from model_trainer.dataset_prep import DatasetPreparator, TrainingExample
from model_trainer.versioning import ModelVersioner


@dataclass
class TrainingConfig:
    """Training configuration."""
    framework: str  # "huggingface", "pytorch", etc.
    model_name: Optional[str] = None
    epochs: int = 3
    batch_size: int = 8
    learning_rate: float = 5e-5
    output_dir: str = "output"
    hyperparameters: Optional[Dict[str, Any]] = None


@dataclass
class ModelCheckpoint:
    """Model checkpoint information."""
    path: str
    version: str
    framework: str
    metrics: Dict[str, float]
    metadata: Dict[str, Any]


@dataclass
class TrainingMetrics:
    """Training metrics."""
    loss: List[float]
    accuracy: Optional[List[float]] = None
    epoch: int = 0
    step: int = 0
    custom_metrics: Optional[Dict[str, List[float]]] = None


class ModelTrainer:
    """
    Main model trainer class for training models.
    """

    def __init__(
        self,
        checkpoint_dir: str = "checkpoints",
        enable_metrics: bool = True
    ):
        """
        Initialize model trainer.

        Args:
            checkpoint_dir: Directory for checkpoints
            enable_metrics: Enable Prometheus metrics
        """
        self.enable_metrics = enable_metrics
        self.dataset_prep = DatasetPreparator(enable_metrics=enable_metrics)
        self.versioner = ModelVersioner(
            checkpoint_dir=checkpoint_dir,
            enable_metrics=enable_metrics
        )
        if enable_metrics:
            from model_trainer.metrics import MetricsCollector
            self.metrics = MetricsCollector()
        else:
            self.metrics = None

    def prepare_dataset(
        self,
        prompts: List[str],
        outputs: List[str],
        **kwargs
    ) -> List[TrainingExample]:
        """
        Prepare training dataset from prompts and outputs.

        Args:
            prompts: List of prompt strings
            outputs: List of output strings
            **kwargs: Additional options

        Returns:
            List of TrainingExample objects
        """
        return self.dataset_prep.prepare_dataset(prompts, outputs, **kwargs)

    def train(
        self,
        examples: List[TrainingExample],
        config: TrainingConfig
    ) -> ModelCheckpoint:
        """
        Train a model.

        Args:
            examples: Training examples
            config: Training configuration

        Returns:
            ModelCheckpoint with checkpoint information

        Raises:
            NotImplementedError: If framework not supported
        """
        start_time = time.time()
        status = "failure"

        try:
            # Update active training runs
            if self.metrics:
                current_active = self._get_active_training_count(config.framework)
                self.metrics.set_active_training_runs(config.framework, current_active + 1)

            # Delegate to framework-specific trainer
            if config.framework == "huggingface":
                checkpoint = self._train_huggingface(examples, config)
            elif config.framework == "pytorch":
                checkpoint = self._train_pytorch(examples, config)
            else:
                raise NotImplementedError(
                    f"Framework {config.framework} not yet implemented. "
                    f"Supported: huggingface, pytorch"
                )

            status = "success"
            return checkpoint

        except Exception as e:
            if self.metrics:
                error_type = type(e).__name__
                self.metrics.track_error(error_type, config.framework)
            raise

        finally:
            # Track metrics
            duration = time.time() - start_time
            if self.metrics:
                self.metrics.track_training_run(config.framework, status)
                self.metrics.track_training_duration(config.framework, duration)
                # Update active training runs
                current_active = self._get_active_training_count(config.framework)
                self.metrics.set_active_training_runs(config.framework, max(0, current_active - 1))

    def _train_huggingface(
        self,
        examples: List[TrainingExample],
        config: TrainingConfig
    ) -> ModelCheckpoint:
        """Train using HuggingFace Transformers."""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
            from model_trainer.integrations.huggingface_integration import HuggingFaceIntegration
        except ImportError:
            raise ImportError(
                "HuggingFace dependencies not installed. "
                "Install with: pip install transformers datasets accelerate"
            )

        integration = HuggingFaceIntegration()
        checkpoint_path, metrics = integration.train(examples, config)

        # Version the checkpoint
        version = self.versioner.version_checkpoint(
            checkpoint_path=checkpoint_path,
            framework="huggingface",
            metadata={
                "model_name": config.model_name,
                "epochs": config.epochs,
                "batch_size": config.batch_size,
                "learning_rate": config.learning_rate,
                "metrics": metrics
            }
        )

        return ModelCheckpoint(
            path=checkpoint_path,
            version=version,
            framework="huggingface",
            metrics=metrics,
            metadata={"config": config.__dict__}
        )

    def _train_pytorch(
        self,
        examples: List[TrainingExample],
        config: TrainingConfig
    ) -> ModelCheckpoint:
        """Train using PyTorch."""
        try:
            from model_trainer.integrations.pytorch_integration import PyTorchIntegration
        except ImportError:
            raise ImportError(
                "PyTorch dependencies not installed. "
                "Install with: pip install torch torchvision"
            )

        integration = PyTorchIntegration()
        checkpoint_path, metrics = integration.train(examples, config)

        # Version the checkpoint
        version = self.versioner.version_checkpoint(
            checkpoint_path=checkpoint_path,
            framework="pytorch",
            metadata={
                "model_name": config.model_name,
                "epochs": config.epochs,
                "batch_size": config.batch_size,
                "learning_rate": config.learning_rate,
                "metrics": metrics
            }
        )

        return ModelCheckpoint(
            path=checkpoint_path,
            version=version,
            framework="pytorch",
            metrics=metrics,
            metadata={"config": config.__dict__}
        )

    def evaluate(
        self,
        model: Any,
        test_set: List[TrainingExample],
        model_version: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Evaluate model performance.

        Args:
            model: Trained model
            test_set: Test dataset
            model_version: Optional model version string

        Returns:
            Dictionary of evaluation metrics
        """
        status = "failure"
        try:
            # Placeholder for evaluation logic
            # In real implementation, this would run inference and calculate metrics
            metrics = {
                "loss": 0.5,
                "accuracy": 0.85,
                "perplexity": 10.2
            }

            status = "success"
            return metrics

        except Exception as e:
            if self.metrics:
                error_type = type(e).__name__
                self.metrics.track_error(error_type, "unknown")
            raise

        finally:
            if self.metrics:
                self.metrics.track_evaluation_run(
                    model_version or "unknown",
                    status
                )

    def _get_active_training_count(self, framework: str) -> int:
        """Get current count of active training runs (placeholder)."""
        # In real implementation, this would track active runs
        return 0

