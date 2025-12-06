"""Tests for model versioning."""

import pytest
import tempfile
from pathlib import Path
from model_trainer.versioning import ModelVersioner


def test_version_checkpoint():
    """Test versioning a checkpoint."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create dummy checkpoint file
        checkpoint_file = Path(tmpdir) / "checkpoint.pt"
        checkpoint_file.write_text("dummy checkpoint data")

        versioner = ModelVersioner(
            checkpoint_dir=str(Path(tmpdir) / "checkpoints"),
            enable_metrics=False
        )

        version = versioner.version_checkpoint(
            checkpoint_path=str(checkpoint_file),
            framework="test",
            metadata={"test": "data"}
        )

        assert version is not None
        assert len(version) > 0

        # Check version exists
        versions = versioner.list_versions("test")
        assert version in versions


def test_list_versions():
    """Test listing versions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        versioner = ModelVersioner(
            checkpoint_dir=str(Path(tmpdir) / "checkpoints"),
            enable_metrics=False
        )

        versions = versioner.list_versions("nonexistent")
        assert versions == []


def test_get_checkpoint_info():
    """Test getting checkpoint info."""
    with tempfile.TemporaryDirectory() as tmpdir:
        checkpoint_file = Path(tmpdir) / "checkpoint.pt"
        checkpoint_file.write_text("dummy data")

        versioner = ModelVersioner(
            checkpoint_dir=str(Path(tmpdir) / "checkpoints"),
            enable_metrics=False
        )

        version = versioner.version_checkpoint(
            checkpoint_path=str(checkpoint_file),
            framework="test"
        )

        info = versioner.get_checkpoint_info("test", version)
        assert info["version"] == version
        assert info["framework"] == "test"

