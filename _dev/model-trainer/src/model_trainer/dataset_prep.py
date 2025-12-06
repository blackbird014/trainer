"""
Dataset preparation from prompts and outputs.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class TrainingExample:
    """Single training example."""
    prompt: str
    output: str
    metadata: Optional[Dict[str, Any]] = None


class DatasetPreparator:
    """Prepare training datasets from prompts and outputs."""

    def __init__(self, enable_metrics: bool = True):
        """
        Initialize dataset preparator.

        Args:
            enable_metrics: Enable Prometheus metrics
        """
        self.enable_metrics = enable_metrics
        if enable_metrics:
            from model_trainer.metrics import MetricsCollector
            self.metrics = MetricsCollector()
        else:
            self.metrics = None

    def prepare_dataset(
        self,
        prompts: List[str],
        outputs: List[str],
        dataset_type: str = "prompt_output",
        **kwargs
    ) -> List[TrainingExample]:
        """
        Prepare dataset from prompts and outputs.

        Args:
            prompts: List of prompt strings
            outputs: List of output strings (must match prompts length)
            dataset_type: Type of dataset (for metrics)
            **kwargs: Additional options

        Returns:
            List of TrainingExample objects

        Raises:
            ValueError: If prompts and outputs lengths don't match
        """
        if len(prompts) != len(outputs):
            raise ValueError(
                f"Prompts ({len(prompts)}) and outputs ({len(outputs)}) "
                f"must have the same length"
            )

        examples = []
        for prompt, output in zip(prompts, outputs):
            example = TrainingExample(
                prompt=prompt,
                output=output,
                metadata=kwargs.get("metadata")
            )
            examples.append(example)

        # Track metrics
        if self.metrics:
            self.metrics.track_dataset_size(dataset_type, len(examples))

        return examples

    def save_dataset(
        self,
        examples: List[TrainingExample],
        output_path: str,
        format: str = "json"
    ):
        """
        Save dataset to file.

        Args:
            examples: List of training examples
            output_path: Path to save dataset
            format: Format to save ("json", "jsonl", "csv")
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        if format == "json":
            data = [
                {
                    "prompt": ex.prompt,
                    "output": ex.output,
                    "metadata": ex.metadata or {}
                }
                for ex in examples
            ]
            output_file.write_text(
                json.dumps(data, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )

        elif format == "jsonl":
            lines = []
            for ex in examples:
                data = {
                    "prompt": ex.prompt,
                    "output": ex.output,
                    "metadata": ex.metadata or {}
                }
                lines.append(json.dumps(data, ensure_ascii=False))
            output_file.write_text("\n".join(lines), encoding='utf-8')

        elif format == "csv":
            import csv
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["prompt", "output", "metadata"])
                for ex in examples:
                    metadata_str = json.dumps(ex.metadata or {}, ensure_ascii=False)
                    writer.writerow([ex.prompt, ex.output, metadata_str])

        else:
            raise ValueError(f"Unsupported format: {format}")

    def load_dataset(self, input_path: str, format: str = "json") -> List[TrainingExample]:
        """
        Load dataset from file.

        Args:
            input_path: Path to dataset file
            format: Format of file ("json", "jsonl", "csv")

        Returns:
            List of TrainingExample objects
        """
        input_file = Path(input_path)
        if not input_file.exists():
            raise FileNotFoundError(f"Dataset file not found: {input_path}")

        examples = []

        if format == "json":
            data = json.loads(input_file.read_text(encoding='utf-8'))
            for item in data:
                examples.append(TrainingExample(
                    prompt=item["prompt"],
                    output=item["output"],
                    metadata=item.get("metadata")
                ))

        elif format == "jsonl":
            for line in input_file.read_text(encoding='utf-8').strip().split('\n'):
                if line.strip():
                    item = json.loads(line)
                    examples.append(TrainingExample(
                        prompt=item["prompt"],
                        output=item["output"],
                        metadata=item.get("metadata")
                    ))

        elif format == "csv":
            import csv
            with open(input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    metadata = json.loads(row.get("metadata", "{}"))
                    examples.append(TrainingExample(
                        prompt=row["prompt"],
                        output=row["output"],
                        metadata=metadata
                    ))

        else:
            raise ValueError(f"Unsupported format: {format}")

        return examples

