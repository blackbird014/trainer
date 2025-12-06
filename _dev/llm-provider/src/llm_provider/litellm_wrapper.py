"""
LiteLLM Wrapper Base Class

Base wrapper around LiteLLM for our specific needs.
Most providers will inherit from this class.
"""

import logging
from typing import Dict, Any, Optional, Iterator
from litellm import completion, completion_cost

from .base import LLMProvider, CompletionResult

logger = logging.getLogger(__name__)


class LiteLLMProvider(LLMProvider):
    """
    Base wrapper around LiteLLM for our specific needs.
    
    This class provides a common implementation for all LiteLLM-based providers,
    handling the conversion between LiteLLM's response format and our
    CompletionResult format.
    """
    
    def __init__(self, provider: str, model: str, **kwargs):
        """
        Initialize LiteLLM-based provider.
        
        Args:
            provider: LiteLLM provider name (e.g., "openai", "anthropic", "bedrock")
            model: Model name (e.g., "gpt-4", "claude-3-opus")
            **kwargs: Additional LiteLLM configuration
        """
        super().__init__(provider_name=provider, model=model, **kwargs)
        self.provider = provider
        self.litellm_model = f"{provider}/{model}"
        self.litellm_config = kwargs
    
    def complete(self, prompt: str, **kwargs) -> CompletionResult:
        """
        Complete a prompt using LiteLLM.
        
        Args:
            prompt: The prompt text to complete
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            CompletionResult with the generated content and metadata
        """
        try:
            # Merge instance config with call-specific kwargs
            call_kwargs = {**self.litellm_config, **kwargs}
            
            # Call LiteLLM
            response = completion(
                model=self.litellm_model,
                messages=[{"role": "user", "content": prompt}],
                **call_kwargs
            )
            
            # Extract content
            content = response.choices[0].message.content
            
            # Extract token usage
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            # Calculate cost
            cost = self._calculate_cost(
                prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
                completion_tokens=response.usage.completion_tokens if response.usage else 0
            )
            
            # Build metadata
            metadata = {
                "response_id": getattr(response, "id", None),
                "model": response.model if hasattr(response, "model") else self.model,
                "created": getattr(response, "created", None),
                "finish_reason": response.choices[0].finish_reason if response.choices else None,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": tokens_used
                } if response.usage else {}
            }
            
            return CompletionResult(
                content=content,
                tokens_used=tokens_used,
                model=self.model,
                provider=self.provider,
                cost=cost,
                metadata=metadata
            )
        
        except Exception as e:
            logger.error(
                f"Error completing prompt with {self.provider}/{self.model}",
                extra={"error": str(e), "provider": self.provider, "model": self.model}
            )
            raise
    
    def stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """
        Stream a completion from LiteLLM.
        
        Args:
            prompt: The prompt text to complete
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Yields:
            str: Chunks of the generated content as they arrive
        """
        try:
            # Merge instance config with call-specific kwargs
            call_kwargs = {**self.litellm_config, **kwargs}
            
            # Ensure stream is True
            call_kwargs["stream"] = True
            
            # Stream from LiteLLM using completion with stream=True
            response_stream = completion(
                model=self.litellm_model,
                messages=[{"role": "user", "content": prompt}],
                **call_kwargs
            )
            
            # Yield content chunks
            for chunk in response_stream:
                if hasattr(chunk, 'choices') and chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta and hasattr(delta, 'content') and delta.content:
                        yield delta.content
                elif hasattr(chunk, 'content'):
                    # Handle different response formats
                    yield chunk.content
        
        except Exception as e:
            logger.error(
                f"Error streaming completion with {self.provider}/{self.model}",
                extra={"error": str(e), "provider": self.provider, "model": self.model}
            )
            raise
    
    def get_cost(self, tokens: int) -> float:
        """
        Calculate the cost for a given number of tokens using LiteLLM's cost calculator.
        
        Args:
            tokens: Number of tokens
            
        Returns:
            Cost in USD
        """
        try:
            # Use LiteLLM's cost calculator
            # Note: completion_cost needs model, prompt_tokens, completion_tokens
            # For a simple estimate, we'll split tokens 50/50
            prompt_tokens = tokens // 2
            completion_tokens = tokens - prompt_tokens
            
            cost = completion_cost(
                model=self.litellm_model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens
            )
            
            return cost if cost else 0.0
        
        except Exception as e:
            logger.warning(
                f"Error calculating cost for {self.provider}/{self.model}",
                extra={"error": str(e), "tokens": tokens}
            )
            # Return 0 if cost calculation fails
            return 0.0
    
    def _calculate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """
        Calculate cost for a specific request.
        
        Args:
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            
        Returns:
            Cost in USD
        """
        try:
            cost = completion_cost(
                model=self.litellm_model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens
            )
            return cost if cost else 0.0
        except Exception:
            return 0.0

