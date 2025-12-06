"""
Ollama Provider

Ollama provider implementation via LiteLLM.
Supports local models running via Ollama.
"""

from typing import Optional
from ...litellm_wrapper import LiteLLMProvider


class OllamaProvider(LiteLLMProvider):
    """
    Ollama provider via LiteLLM.
    
    Supports local models running via Ollama (e.g., llama2, mistral, codellama).
    Requires Ollama to be running locally.
    """
    
    def __init__(
        self,
        model: str = "llama2",
        base_url: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize Ollama provider.
        
        Args:
            model: Model name (default: "llama2")
            base_url: Ollama base URL (default: "http://localhost:11434")
            **kwargs: Additional LiteLLM configuration
        """
        # Set base URL if provided
        if base_url:
            kwargs["api_base"] = base_url
        else:
            kwargs["api_base"] = kwargs.get("api_base", "http://localhost:11434")
        
        super().__init__(
            provider="ollama",
            model=model,
            **kwargs
        )

