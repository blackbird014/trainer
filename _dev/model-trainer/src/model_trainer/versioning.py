"""
Model checkpoint versioning.
"""

from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import json
import hashlib


class ModelVersioner:
    """Version control for model checkpoints."""

    def __init__(self, checkpoint_dir: str = "checkpoints", enable_metrics: bool = True):
        """
        Initialize model versioner.

        Args:
            checkpoint_dir: Directory to store checkpoints
            enable_metrics: Enable Prometheus metrics
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.enable_metrics = enable_metrics
        if enable_metrics:
            from model_trainer.metrics import MetricsCollector
            self.metrics = MetricsCollector()
        else:
            self.metrics = None

    def version_checkpoint(
        self,
        checkpoint_path: str,
        framework: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Version a model checkpoint.

        Args:
            checkpoint_path: Path to checkpoint file
            framework: Framework name (e.g., "huggingface", "pytorch")
            metadata: Optional metadata about the checkpoint

        Returns:
            Version string (e.g., "v1.0.0" or hash-based)
        """
        checkpoint_file = Path(checkpoint_path)
        if not checkpoint_file.exists():
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")

        # Generate version based on timestamp and hash
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_hash = self._calculate_hash(checkpoint_path)
        version = f"{timestamp}_{file_hash[:8]}"

        # Create versioned directory
        version_dir = self.checkpoint_dir / framework / version
        version_dir.mkdir(parents=True, exist_ok=True)

        # Copy checkpoint
        import shutil
        dest_path = version_dir / checkpoint_file.name
        shutil.copy2(checkpoint_path, dest_path)

        # Save metadata
        metadata_file = version_dir / "metadata.json"
        metadata_data = {
            "version": version,
            "framework": framework,
            "original_path": str(checkpoint_path),
            "timestamp": timestamp,
            "file_hash": file_hash,
            "metadata": metadata or {}
        }
        metadata_file.write_text(
            json.dumps(metadata_data, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )

        # Track metrics
        if self.metrics:
            self.metrics.track_model_version(framework)
            checkpoint_size = checkpoint_file.stat().st_size
            self.metrics.track_checkpoint_size(framework, checkpoint_size)

        return version

    def get_checkpoint_info(self, framework: str, version: str) -> Dict[str, Any]:
        """
        Get information about a versioned checkpoint.

        Args:
            framework: Framework name
            version: Version string

        Returns:
            Dictionary with checkpoint information
        """
        version_dir = self.checkpoint_dir / framework / version
        metadata_file = version_dir / "metadata.json"

        if not metadata_file.exists():
            raise FileNotFoundError(
                f"Checkpoint version not found: {framework}/{version}"
            )

        return json.loads(metadata_file.read_text(encoding='utf-8'))

    def list_versions(self, framework: str) -> List[str]:
        """
        List all versions for a framework.

        Args:
            framework: Framework name

        Returns:
            List of version strings
        """
        framework_dir = self.checkpoint_dir / framework
        if not framework_dir.exists():
            return []

        versions = []
        for version_dir in framework_dir.iterdir():
            if version_dir.is_dir():
                versions.append(version_dir.name)

        return sorted(versions, reverse=True)  # Most recent first

    def _calculate_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file."""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

