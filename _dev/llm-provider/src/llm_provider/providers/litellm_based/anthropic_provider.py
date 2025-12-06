"""
Anthropic Provider

Anthropic provider implementation via LiteLLM.
Supports Claude 3 models (Opus, Sonnet, Haiku).
"""

from typing import Optional
from ...litellm_wrapper import LiteLLMProvider


class AnthropicProvider(LiteLLMProvider):
    """
    Anthropic provider via LiteLLM.
    
    Supports Claude 3 models (Opus, Sonnet, Haiku).
    Authentication via ANTHROPIC_API_KEY environment variable or api_key parameter.
    """
    
    def __init__(
        self,
        model: str = "claude-3-opus-20240229",
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize Anthropic provider.
        
        Args:
            model: Model name (default: "claude-3-opus-20240229")
            api_key: Anthropic API key (default: from ANTHROPIC_API_KEY env var)
            **kwargs: Additional LiteLLM configuration
        """
        # Set API key if provided
        if api_key:
            kwargs["api_key"] = api_key
        
        super().__init__(
            provider="anthropic",
            model=model,
            **kwargs
        )

