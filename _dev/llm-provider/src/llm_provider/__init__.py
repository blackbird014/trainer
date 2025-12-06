"""
LLM Provider Abstraction Layer

Unified interface for multiple LLM providers via LiteLLM.
"""

from .base import LLMProvider, CompletionResult
from .litellm_wrapper import LiteLLMProvider
from .registry import (
    ProviderRegistry,
    get_registry,
    register_provider,
    create_provider,
    list_providers
)
from .config import ProviderConfig, LLMProviderConfig
from .utils import (
    estimate_tokens,
    format_prompt,
    validate_provider_config,
    merge_provider_configs,
    get_provider_info,
    calculate_total_cost,
    calculate_total_tokens
)

# Import providers
from .providers import (
    OpenAIProvider,
    AnthropicProvider,
    OllamaProvider,
    AWSBedrockProvider,
    GoogleVertexProvider,
    AzureOpenAIProvider,
    HuggingFaceProvider,
)

from .providers.direct import AWSSageMakerProvider

__all__ = [
    # Base classes
    "LLMProvider",
    "CompletionResult",
    "LiteLLMProvider",
    
    # Registry
    "ProviderRegistry",
    "get_registry",
    "register_provider",
    "create_provider",
    "list_providers",
    
    # Configuration
    "ProviderConfig",
    "LLMProviderConfig",
    
    # Utilities
    "estimate_tokens",
    "format_prompt",
    "validate_provider_config",
    "merge_provider_configs",
    "get_provider_info",
    "calculate_total_cost",
    "calculate_total_tokens",
    
    # Providers (LiteLLM-based)
    "OpenAIProvider",
    "AnthropicProvider",
    "OllamaProvider",
    "AWSBedrockProvider",
    "GoogleVertexProvider",
    "AzureOpenAIProvider",
    "HuggingFaceProvider",
    
    # Providers (Direct)
    "AWSSageMakerProvider",
]

# Auto-register built-in providers
_registry = get_registry()
_registry.register("openai", OpenAIProvider, is_default=True)
_registry.register("anthropic", AnthropicProvider)
_registry.register("ollama", OllamaProvider)
_registry.register("bedrock", AWSBedrockProvider)
_registry.register("vertex", GoogleVertexProvider)
_registry.register("azure", AzureOpenAIProvider)
_registry.register("huggingface", HuggingFaceProvider)
_registry.register("sagemaker", AWSSageMakerProvider)

