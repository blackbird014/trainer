"""Tests for ModelTrainer."""

import pytest
from model_trainer import ModelTrainer, TrainingConfig, TrainingExample


def test_trainer_init():
    """Test trainer initialization."""
    trainer = ModelTrainer(enable_metrics=False)
    assert trainer.enable_metrics is False


def test_prepare_dataset():
    """Test preparing dataset via trainer."""
    trainer = ModelTrainer(enable_metrics=False)
    prompts = ["P1", "P2"]
    outputs = ["O1", "O2"]

    examples = trainer.prepare_dataset(prompts, outputs)
    assert len(examples) == 2


def test_train_not_implemented_framework():
    """Test error for unsupported framework."""
    trainer = ModelTrainer(enable_metrics=False)
    examples = [
        TrainingExample(prompt="P1", output="O1")
    ]
    config = TrainingConfig(framework="unsupported")

    with pytest.raises(NotImplementedError):
        trainer.train(examples, config)


def test_evaluate():
    """Test evaluation."""
    trainer = ModelTrainer(enable_metrics=False)
    test_set = [
        TrainingExample(prompt="P1", output="O1")
    ]

    # Evaluation is a placeholder, should not raise
    metrics = trainer.evaluate(model=None, test_set=test_set)
    assert isinstance(metrics, dict)

