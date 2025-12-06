"""
HuggingFace Transformers integration.
"""

from typing import List, Dict, Any
from pathlib import Path

from model_trainer.dataset_prep import TrainingExample
from model_trainer.trainer import TrainingConfig


class HuggingFaceIntegration:
    """Integration with HuggingFace Transformers."""

    def train(
        self,
        examples: List[TrainingExample],
        config: TrainingConfig
    ) -> tuple[str, Dict[str, float]]:
        """
        Train model using HuggingFace.

        Args:
            examples: Training examples
            config: Training configuration

        Returns:
            Tuple of (checkpoint_path, metrics_dict)
        """
        try:
            from transformers import (
                AutoTokenizer,
                AutoModelForCausalLM,
                TrainingArguments,
                Trainer,
                DataCollatorForLanguageModeling
            )
            from datasets import Dataset
        except ImportError:
            raise ImportError(
                "HuggingFace dependencies not installed. "
                "Install with: pip install transformers datasets accelerate"
            )

        # Prepare dataset
        dataset_dict = {
            "text": [
                f"{ex.prompt} {ex.output}" for ex in examples
            ]
        }
        dataset = Dataset.from_dict(dataset_dict)

        # Load tokenizer and model
        model_name = config.model_name or "gpt2"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)

        # Set pad token if not set
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        # Tokenize dataset
        def tokenize_function(examples):
            return tokenizer(
                examples["text"],
                truncation=True,
                max_length=512,
                padding="max_length"
            )

        tokenized_dataset = dataset.map(tokenize_function, batched=True)

        # Training arguments
        output_dir = Path(config.output_dir) / "huggingface"
        output_dir.mkdir(parents=True, exist_ok=True)

        training_args = TrainingArguments(
            output_dir=str(output_dir),
            num_train_epochs=config.epochs,
            per_device_train_batch_size=config.batch_size,
            learning_rate=config.learning_rate,
            save_strategy="epoch",
            logging_steps=10,
            **config.hyperparameters or {}
        )

        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False  # Causal LM, not masked LM
        )

        # Trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_dataset,
            data_collator=data_collator,
        )

        # Train
        train_result = trainer.train()

        # Save final checkpoint
        checkpoint_path = output_dir / "final"
        trainer.save_model(str(checkpoint_path))
        tokenizer.save_pretrained(str(checkpoint_path))

        # Extract metrics
        metrics = {
            "train_loss": train_result.training_loss,
            "train_runtime": train_result.metrics.get("train_runtime", 0),
            "train_samples_per_second": train_result.metrics.get("train_samples_per_second", 0),
        }

        return str(checkpoint_path), metrics

