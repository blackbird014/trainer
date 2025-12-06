"""
Common Utilities

Utility functions for LLM provider operations.
"""

import logging
from typing import Dict, Any, Optional, List
from .base import LLMProvider, CompletionResult

logger = logging.getLogger(__name__)


def estimate_tokens(text: str, model: Optional[str] = None) -> int:
    """
    Estimate token count for text.
    
    This is a rough estimation. For accurate counts, use the provider's
    tokenizer if available.
    
    Args:
        text: Text to estimate tokens for
        model: Model name (for model-specific estimation)
        
    Returns:
        Estimated token count
    """
    # Rough estimation: ~4 characters per token for most models
    # Some models (like GPT-4) use ~3.5 characters per token
    chars_per_token = 3.5 if model and "gpt-4" in model.lower() else 4.0
    
    return int(len(text) / chars_per_token)


def format_prompt(
    system_prompt: Optional[str] = None,
    user_prompt: str = "",
    messages: Optional[List[Dict[str, str]]] = None
) -> str:
    """
    Format a prompt for LLM consumption.
    
    Args:
        system_prompt: System prompt (optional)
        user_prompt: User prompt
        messages: List of message dicts with 'role' and 'content' (optional)
        
    Returns:
        Formatted prompt string
    """
    if messages:
        # Format messages
        formatted = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            formatted.append(f"{role.capitalize()}: {content}")
        return "\n\n".join(formatted)
    
    # Format with system and user prompts
    parts = []
    if system_prompt:
        parts.append(f"System: {system_prompt}")
    if user_prompt:
        parts.append(f"User: {user_prompt}")
    
    return "\n\n".join(parts) if parts else ""


def validate_provider_config(config: Dict[str, Any]) -> bool:
    """
    Validate provider configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        True if valid, False otherwise
    """
    required_keys = ["provider", "model"]
    
    for key in required_keys:
        if key not in config:
            logger.error(f"Missing required configuration key: {key}")
            return False
    
    return True


def merge_provider_configs(
    base_config: Dict[str, Any],
    override_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Merge two provider configurations.
    
    Args:
        base_config: Base configuration
        override_config: Configuration to override with
        
    Returns:
        Merged configuration
    """
    merged = base_config.copy()
    merged.update(override_config)
    return merged


def get_provider_info(provider: LLMProvider) -> Dict[str, Any]:
    """
    Get information about a provider.
    
    Args:
        provider: LLMProvider instance
        
    Returns:
        Dictionary with provider information
    """
    return {
        "provider_name": provider.provider_name,
        "model": provider.model,
        "provider_type": provider.__class__.__name__,
        "config_keys": list(provider.config.keys())
    }


def calculate_total_cost(results: List[CompletionResult]) -> float:
    """
    Calculate total cost from multiple completion results.
    
    Args:
        results: List of CompletionResult instances
        
    Returns:
        Total cost in USD
    """
    return sum(result.cost for result in results)


def calculate_total_tokens(results: List[CompletionResult]) -> int:
    """
    Calculate total tokens from multiple completion results.
    
    Args:
        results: List of CompletionResult instances
        
    Returns:
        Total token count
    """
    return sum(result.tokens_used for result in results)

