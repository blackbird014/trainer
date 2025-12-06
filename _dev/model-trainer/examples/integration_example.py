#!/usr/bin/env python3
"""
Integration example showing model-trainer with other modules.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from prompt_manager import PromptManager
    from llm_provider import create_provider
    from model_trainer import ModelTrainer, TrainingConfig
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Make sure all modules are installed")
    sys.exit(1)


def integration_example():
    """Example integrating prompt-manager, llm-provider, and model-trainer."""
    print("=" * 80)
    print("Model Trainer Integration Example")
    print("=" * 80)
    print()

    # 1. Generate training data using prompt-manager and llm-provider
    print("Step 1: Generating training data...")
    prompts = [
        "Analyze company AAPL",
        "Analyze company NVDA",
        "Analyze company MSFT"
    ]

    # In real scenario, would use LLM to generate outputs
    outputs = [
        "AAPL shows strong financial performance with high revenue growth.",
        "NVDA demonstrates leadership in AI chip market.",
        "MSFT has diversified revenue streams across cloud and software."
    ]

    print(f"✓ Generated {len(prompts)} prompt-output pairs")
    print()

    # 2. Prepare dataset
    print("Step 2: Preparing training dataset...")
    trainer = ModelTrainer(enable_metrics=True)
    examples = trainer.prepare_dataset(prompts, outputs)
    print(f"✓ Prepared dataset with {len(examples)} examples")
    print()

    # 3. Save dataset
    print("Step 3: Saving dataset...")
    trainer.dataset_prep.save_dataset(examples, "training_dataset.json", format="json")
    print("✓ Saved dataset to training_dataset.json")
    print()

    # 4. Version checkpoint (simulated)
    print("Step 4: Versioning checkpoint...")
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as tmpdir:
        checkpoint_file = Path(tmpdir) / "model.pt"
        checkpoint_file.write_text("dummy checkpoint")

        version = trainer.versioner.version_checkpoint(
            checkpoint_path=str(checkpoint_file),
            framework="test",
            metadata={"source": "integration_example"}
        )
        print(f"✓ Versioned checkpoint: {version}")
    print()

    print("=" * 80)
    print("Integration Complete!")
    print("=" * 80)
    print()
    print("Workflow:")
    print("  1. Generate prompts/outputs (prompt-manager + llm-provider)")
    print("  2. Prepare dataset (model-trainer)")
    print("  3. Train model (model-trainer)")
    print("  4. Version checkpoint (model-trainer)")
    print("  5. Evaluate model (model-trainer)")


if __name__ == "__main__":
    try:
        integration_example()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

