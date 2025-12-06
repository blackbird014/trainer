"""
Provider Registry

Factory and registry for creating and managing LLM providers.
"""

import logging
from typing import Dict, Any, Optional, Type, List
from .base import LLMProvider

logger = logging.getLogger(__name__)


class ProviderRegistry:
    """
    Registry for LLM providers.
    
    Allows registration and creation of providers by name.
    """
    
    def __init__(self):
        """Initialize the provider registry."""
        self._providers: Dict[str, Type[LLMProvider]] = {}
        self._default_provider: Optional[str] = None
    
    def register(
        self,
        name: str,
        provider_class: Type[LLMProvider],
        is_default: bool = False
    ):
        """
        Register a provider class.
        
        Args:
            name: Provider name (e.g., "openai", "anthropic")
            provider_class: Provider class that inherits from LLMProvider
            is_default: Whether this should be the default provider
        """
        if not issubclass(provider_class, LLMProvider):
            raise ValueError(
                f"Provider class must inherit from LLMProvider, got {provider_class}"
            )
        
        self._providers[name] = provider_class
        
        if is_default:
            self._default_provider = name
        
        logger.debug(f"Registered provider: {name}")
    
    def create(
        self,
        provider_name: str,
        **kwargs
    ) -> LLMProvider:
        """
        Create a provider instance.
        
        Args:
            provider_name: Name of the provider to create
            **kwargs: Provider-specific configuration
            
        Returns:
            LLMProvider instance
            
        Raises:
            ValueError: If provider is not registered
        """
        if provider_name not in self._providers:
            available = ", ".join(self._providers.keys())
            raise ValueError(
                f"Provider '{provider_name}' not found. Available providers: {available}"
            )
        
        provider_class = self._providers[provider_name]
        
        # Automatically pass provider_name if not already in kwargs
        if "provider_name" not in kwargs:
            kwargs["provider_name"] = provider_name
        
        try:
            return provider_class(**kwargs)
        except Exception as e:
            logger.error(
                f"Failed to create provider {provider_name}",
                extra={"error": str(e), "provider": provider_name}
            )
            raise
    
    def list_providers(self) -> List[str]:
        """
        List all registered provider names.
        
        Returns:
            List of provider names
        """
        return list(self._providers.keys())
    
    def get_default(self) -> Optional[str]:
        """
        Get the default provider name.
        
        Returns:
            Default provider name or None
        """
        return self._default_provider
    
    def set_default(self, provider_name: str):
        """
        Set the default provider.
        
        Args:
            provider_name: Name of the provider to set as default
            
        Raises:
            ValueError: If provider is not registered
        """
        if provider_name not in self._providers:
            raise ValueError(f"Provider '{provider_name}' is not registered")
        
        self._default_provider = provider_name
        logger.debug(f"Set default provider: {provider_name}")


# Global registry instance
_registry = ProviderRegistry()


def get_registry() -> ProviderRegistry:
    """
    Get the global provider registry.
    
    Returns:
        ProviderRegistry instance
    """
    return _registry


def register_provider(
    name: str,
    provider_class: Type[LLMProvider],
    is_default: bool = False
):
    """
    Register a provider in the global registry.
    
    Args:
        name: Provider name
        provider_class: Provider class
        is_default: Whether this should be the default provider
    """
    _registry.register(name, provider_class, is_default)


def create_provider(provider_name: str, **kwargs) -> LLMProvider:
    """
    Create a provider instance from the global registry.
    
    Args:
        provider_name: Name of the provider
        **kwargs: Provider-specific configuration
        
    Returns:
        LLMProvider instance
    """
    return _registry.create(provider_name, **kwargs)


def list_providers() -> List[str]:
    """
    List all registered providers.
    
    Returns:
        List of provider names
    """
    return _registry.list_providers()

