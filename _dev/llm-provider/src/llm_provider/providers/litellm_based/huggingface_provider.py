"""
HuggingFace Provider

HuggingFace provider implementation via LiteLLM.
Supports HuggingFace models via HuggingFace Inference API.
"""

from typing import Optional
from ...litellm_wrapper import LiteLLMProvider


class HuggingFaceProvider(LiteLLMProvider):
    """
    HuggingFace provider via LiteLLM.
    
    Supports HuggingFace models via HuggingFace Inference API.
    Authentication via HUGGINGFACE_API_KEY environment variable or api_key parameter.
    """
    
    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize HuggingFace provider.
        
        Args:
            model: HuggingFace model ID (e.g., "meta-llama/Llama-2-7b-chat-hf")
            api_key: HuggingFace API key (default: from HUGGINGFACE_API_KEY env var)
            **kwargs: Additional LiteLLM configuration
        """
        # Set API key if provided
        if api_key:
            kwargs["api_key"] = api_key
        
        super().__init__(
            provider="huggingface",
            model=model,
            **kwargs
        )

