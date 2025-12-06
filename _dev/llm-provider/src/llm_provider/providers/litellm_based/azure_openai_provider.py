"""
Azure OpenAI Provider

Azure OpenAI provider implementation via LiteLLM.
Supports GPT-4, GPT-3.5, and other Azure OpenAI models.
"""

from typing import Optional
from ...litellm_wrapper import LiteLLMProvider


class AzureOpenAIProvider(LiteLLMProvider):
    """
    Azure OpenAI provider via LiteLLM.
    
    Supports GPT-4, GPT-3.5, and other Azure OpenAI models.
    Authentication via Azure API key or Azure AD.
    """
    
    def __init__(
        self,
        model: str,
        endpoint: str,
        api_key: Optional[str] = None,
        api_version: str = "2024-02-15-preview",
        **kwargs
    ):
        """
        Initialize Azure OpenAI provider.
        
        Args:
            model: Azure deployment name (e.g., "gpt-4", "gpt-35-turbo")
            endpoint: Azure OpenAI endpoint URL
            api_key: Azure API key (optional, can use Azure AD instead)
            api_version: API version (default: "2024-02-15-preview")
            **kwargs: Additional LiteLLM configuration
        """
        # Set Azure configuration
        kwargs["api_base"] = endpoint
        kwargs["api_version"] = api_version
        
        if api_key:
            kwargs["api_key"] = api_key
        
        super().__init__(
            provider="azure",
            model=model,
            **kwargs
        )

