"""Tests for dataset preparation."""

import pytest
import tempfile
from pathlib import Path
from model_trainer.dataset_prep import DatasetPreparator, TrainingExample


def test_prepare_dataset():
    """Test preparing dataset from prompts and outputs."""
    preparator = DatasetPreparator(enable_metrics=False)
    prompts = ["Prompt 1", "Prompt 2"]
    outputs = ["Output 1", "Output 2"]

    examples = preparator.prepare_dataset(prompts, outputs)
    assert len(examples) == 2
    assert examples[0].prompt == "Prompt 1"
    assert examples[0].output == "Output 1"


def test_prepare_dataset_mismatched_lengths():
    """Test error when prompts and outputs don't match."""
    preparator = DatasetPreparator(enable_metrics=False)
    prompts = ["Prompt 1", "Prompt 2"]
    outputs = ["Output 1"]

    with pytest.raises(ValueError, match="must have the same length"):
        preparator.prepare_dataset(prompts, outputs)


def test_save_and_load_json():
    """Test saving and loading JSON dataset."""
    preparator = DatasetPreparator(enable_metrics=False)
    examples = [
        TrainingExample(prompt="P1", output="O1"),
        TrainingExample(prompt="P2", output="O2")
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "dataset.json"
        preparator.save_dataset(examples, str(output_path), format="json")

        loaded = preparator.load_dataset(str(output_path), format="json")
        assert len(loaded) == 2
        assert loaded[0].prompt == "P1"
        assert loaded[1].output == "O2"


def test_save_and_load_jsonl():
    """Test saving and loading JSONL dataset."""
    preparator = DatasetPreparator(enable_metrics=False)
    examples = [
        TrainingExample(prompt="P1", output="O1")
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "dataset.jsonl"
        preparator.save_dataset(examples, str(output_path), format="jsonl")

        loaded = preparator.load_dataset(str(output_path), format="jsonl")
        assert len(loaded) == 1
        assert loaded[0].prompt == "P1"

