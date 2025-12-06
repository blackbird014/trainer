"""
Configuration Management

Configuration management for LLM providers.
Supports YAML, JSON, and environment variable configuration.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

logger = logging.getLogger(__name__)


class ProviderConfig:
    """
    Configuration for an LLM provider.
    
    Supports loading from files, environment variables, and dictionaries.
    """
    
    def __init__(
        self,
        provider: str,
        model: str,
        **kwargs
    ):
        """
        Initialize provider configuration.
        
        Args:
            provider: Provider name
            model: Model name
            **kwargs: Additional configuration
        """
        self.provider = provider
        self.model = model
        self.config = kwargs
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Configuration dictionary
        """
        return {
            "provider": self.provider,
            "model": self.model,
            **self.config
        }
    
    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "ProviderConfig":
        """
        Create configuration from dictionary.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            ProviderConfig instance
        """
        provider = config.pop("provider")
        model = config.pop("model")
        return cls(provider=provider, model=model, **config)
    
    @classmethod
    def from_env(cls, prefix: str = "LLM_") -> Optional["ProviderConfig"]:
        """
        Create configuration from environment variables.
        
        Args:
            prefix: Environment variable prefix (default: "LLM_")
            
        Returns:
            ProviderConfig instance or None if not configured
        """
        provider = os.getenv(f"{prefix}PROVIDER")
        model = os.getenv(f"{prefix}MODEL")
        
        if not provider or not model:
            return None
        
        # Extract other config from environment
        config = {}
        for key, value in os.environ.items():
            if key.startswith(prefix) and key not in [f"{prefix}PROVIDER", f"{prefix}MODEL"]:
                # Remove prefix and convert to lowercase
                config_key = key[len(prefix):].lower()
                config[config_key] = value
        
        return cls(provider=provider, model=model, **config)
    
    @classmethod
    def from_file(cls, config_path: str) -> "ProviderConfig":
        """
        Load configuration from file (YAML or JSON).
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            ProviderConfig instance
        """
        path = Path(config_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(path, 'r') as f:
            if path.suffix.lower() in ['.yaml', '.yml']:
                if not YAML_AVAILABLE:
                    raise ImportError(
                        "PyYAML is required for YAML configuration files. "
                        "Install it with: pip install pyyaml"
                    )
                config_dict = yaml.safe_load(f)
            elif path.suffix.lower() == '.json':
                config_dict = json.load(f)
            else:
                raise ValueError(
                    f"Unsupported configuration file format: {path.suffix}. "
                    "Supported formats: .yaml, .yml, .json"
                )
        
        return cls.from_dict(config_dict)


class LLMProviderConfig:
    """
    Configuration manager for multiple LLM providers.
    
    Supports loading from files and environment variables.
    """
    
    def __init__(self):
        """Initialize configuration manager."""
        self.providers: Dict[str, ProviderConfig] = {}
        self.default_provider: Optional[str] = None
    
    def add_provider(self, name: str, config: ProviderConfig):
        """
        Add a provider configuration.
        
        Args:
            name: Provider name
            config: Provider configuration
        """
        self.providers[name] = config
    
    def get_provider(self, name: Optional[str] = None) -> Optional[ProviderConfig]:
        """
        Get provider configuration.
        
        Args:
            name: Provider name (uses default if None)
            
        Returns:
            ProviderConfig instance or None
        """
        if name is None:
            name = self.default_provider
        
        return self.providers.get(name) if name else None
    
    def set_default(self, name: str):
        """
        Set default provider.
        
        Args:
            name: Provider name
        """
        if name not in self.providers:
            raise ValueError(f"Provider '{name}' not found in configuration")
        self.default_provider = name
    
    @classmethod
    def from_file(cls, config_path: str) -> "LLMProviderConfig":
        """
        Load configuration from file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            LLMProviderConfig instance
        """
        path = Path(config_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(path, 'r') as f:
            if path.suffix.lower() in ['.yaml', '.yml']:
                if not YAML_AVAILABLE:
                    raise ImportError("PyYAML is required for YAML configuration files")
                config_dict = yaml.safe_load(f)
            elif path.suffix.lower() == '.json':
                config_dict = json.load(f)
            else:
                raise ValueError(f"Unsupported configuration file format: {path.suffix}")
        
        manager = cls()
        
        # Load providers
        providers_config = config_dict.get("providers", {})
        for name, provider_config in providers_config.items():
            config = ProviderConfig.from_dict(provider_config)
            manager.add_provider(name, config)
        
        # Set default provider
        if "default_provider" in config_dict:
            manager.set_default(config_dict["default_provider"])
        
        return manager
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Configuration dictionary
        """
        return {
            "providers": {
                name: config.to_dict()
                for name, config in self.providers.items()
            },
            "default_provider": self.default_provider
        }

