"""
Base LLM Provider Abstraction

Defines the abstract interface for all LLM providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Iterator, List
from datetime import datetime


@dataclass
class CompletionResult:
    """Result of an LLM completion request."""
    
    content: str
    tokens_used: int
    model: str
    provider: str
    cost: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate result data."""
        if self.tokens_used < 0:
            raise ValueError("tokens_used must be non-negative")
        if self.cost < 0:
            raise ValueError("cost must be non-negative")
        if not self.content:
            raise ValueError("content cannot be empty")


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    All LLM providers must implement this interface to ensure
    consistent behavior across different providers.
    """
    
    def __init__(self, provider_name: str, model: str, **kwargs):
        """
        Initialize LLM provider.
        
        Args:
            provider_name: Name of the provider (e.g., "openai", "anthropic")
            model: Model name (e.g., "gpt-4", "claude-3-opus")
            **kwargs: Provider-specific configuration
        """
        self.provider_name = provider_name
        self.model = model
        self.config = kwargs
    
    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> CompletionResult:
        """
        Complete a prompt using the LLM.
        
        Args:
            prompt: The prompt text to complete
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            CompletionResult with the generated content and metadata
            
        Raises:
            Exception: If the completion fails
        """
        pass
    
    @abstractmethod
    def stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """
        Stream a completion from the LLM.
        
        Args:
            prompt: The prompt text to complete
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Yields:
            str: Chunks of the generated content as they arrive
        """
        pass
    
    @abstractmethod
    def get_cost(self, tokens: int) -> float:
        """
        Calculate the cost for a given number of tokens.
        
        Args:
            tokens: Number of tokens
            
        Returns:
            Cost in USD
        """
        pass
    
    def list_models(self) -> List[str]:
        """
        List available models for this provider.
        
        Returns:
            List of available model names
            
        Raises:
            NotImplementedError: If the provider doesn't support model listing
        """
        raise NotImplementedError(
            f"Provider {self.provider_name} does not support listing models"
        )
    
    def deploy_model(self, model_path: str, **kwargs) -> str:
        """
        Deploy a custom model (for providers that support it).
        
        Args:
            model_path: Path to the model
            **kwargs: Deployment-specific parameters
            
        Returns:
            Deployment identifier (endpoint name, model ID, etc.)
            
        Raises:
            NotImplementedError: If the provider doesn't support model deployment
        """
        raise NotImplementedError(
            f"Provider {self.provider_name} does not support model deployment"
        )
    
    def __repr__(self) -> str:
        """String representation of the provider."""
        return f"{self.__class__.__name__}(provider={self.provider_name}, model={self.model})"

