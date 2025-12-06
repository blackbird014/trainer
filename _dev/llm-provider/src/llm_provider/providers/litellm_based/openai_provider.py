"""
OpenAI Provider

OpenAI provider implementation via LiteLLM.
Supports GPT-4, GPT-3.5, and other OpenAI models.
"""

from typing import Optional
from ...litellm_wrapper import LiteLLMProvider


class OpenAIProvider(LiteLLMProvider):
    """
    OpenAI provider via LiteLLM.
    
    Supports GPT-4, GPT-3.5, and other OpenAI models.
    Authentication via OPENAI_API_KEY environment variable or api_key parameter.
    """
    
    def __init__(
        self,
        model: str = "gpt-4",
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize OpenAI provider.
        
        Args:
            model: Model name (default: "gpt-4")
            api_key: OpenAI API key (default: from OPENAI_API_KEY env var)
            **kwargs: Additional LiteLLM configuration
        """
        # Set API key if provided
        if api_key:
            kwargs["api_key"] = api_key
        
        super().__init__(
            provider="openai",
            model=model,
            **kwargs
        )

