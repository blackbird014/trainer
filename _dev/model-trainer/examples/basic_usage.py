#!/usr/bin/env python3
"""
Basic usage examples for model-trainer module.
"""

from model_trainer import ModelTrainer, TrainingConfig, TrainingExample


def example_prepare_dataset():
    """Example: Prepare training dataset."""
    print("=" * 60)
    print("Prepare Dataset Example")
    print("=" * 60)

    trainer = ModelTrainer(enable_metrics=False)

    prompts = [
        "Analyze the following company:",
        "What are the key metrics for",
        "Provide insights on"
    ]
    outputs = [
        "Company analysis shows strong fundamentals.",
        "Key metrics include revenue growth and profitability.",
        "Insights indicate positive market position."
    ]

    examples = trainer.prepare_dataset(prompts, outputs)
    print(f"✓ Prepared {len(examples)} training examples")
    print(f"  Example 1: {examples[0].prompt[:50]}...")


def example_save_dataset():
    """Example: Save dataset to file."""
    print("\n" + "=" * 60)
    print("Save Dataset Example")
    print("=" * 60)

    trainer = ModelTrainer(enable_metrics=False)
    examples = trainer.prepare_dataset(
        ["P1", "P2"],
        ["O1", "O2"]
    )

    # Save as JSON
    trainer.dataset_prep.save_dataset(
        examples,
        "dataset.json",
        format="json"
    )
    print("✓ Saved dataset to dataset.json")

    # Load it back
    loaded = trainer.dataset_prep.load_dataset("dataset.json", format="json")
    print(f"✓ Loaded {len(loaded)} examples from dataset.json")


def example_version_checkpoint():
    """Example: Version a model checkpoint."""
    print("\n" + "=" * 60)
    print("Version Checkpoint Example")
    print("=" * 60)

    import tempfile
    from pathlib import Path

    trainer = ModelTrainer(enable_metrics=False)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create dummy checkpoint
        checkpoint_file = Path(tmpdir) / "model.pt"
        checkpoint_file.write_text("dummy model data")

        version = trainer.versioner.version_checkpoint(
            checkpoint_path=str(checkpoint_file),
            framework="test",
            metadata={"epochs": 3, "loss": 0.5}
        )
        print(f"✓ Versioned checkpoint: {version}")

        # List versions
        versions = trainer.versioner.list_versions("test")
        print(f"✓ Found {len(versions)} versions: {versions}")


def example_evaluate():
    """Example: Evaluate a model."""
    print("\n" + "=" * 60)
    print("Evaluate Model Example")
    print("=" * 60)

    trainer = ModelTrainer(enable_metrics=False)

    test_set = [
        TrainingExample(prompt="Test prompt", output="Expected output")
    ]

    metrics = trainer.evaluate(model=None, test_set=test_set)
    print(f"✓ Evaluation metrics: {metrics}")


if __name__ == "__main__":
    try:
        example_prepare_dataset()
        example_save_dataset()
        example_version_checkpoint()
        example_evaluate()
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()

