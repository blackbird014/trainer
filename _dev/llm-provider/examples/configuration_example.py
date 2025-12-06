#!/usr/bin/env python3
"""
Configuration Example

Demonstrates loading and using provider configurations from files.
"""

import os
import json
from pathlib import Path
from llm_provider import (
    ProviderConfig,
    LLMProviderConfig,
    create_provider
)


def example_env_config():
    """Load configuration from environment variables"""
    print("=" * 60)
    print("Environment Variable Configuration")
    print("=" * 60)
    
    # Set environment variables (for demonstration)
    # In practice, these would be set in your shell
    os.environ.setdefault("LLM_PROVIDER", "openai")
    os.environ.setdefault("LLM_MODEL", "gpt-4")
    
    config = ProviderConfig.from_env(prefix="LLM_")
    
    if config:
        print(f"\nLoaded config from environment:")
        print(f"  Provider: {config.provider}")
        print(f"  Model: {config.model}")
        print(f"  Config: {config.config}")
    else:
        print("\nNo LLM configuration found in environment variables")
        print("Set LLM_PROVIDER and LLM_MODEL to use this feature")


def example_dict_config():
    """Create configuration from dictionary"""
    print("\n" + "=" * 60)
    print("Dictionary Configuration")
    print("=" * 60)
    
    config_dict = {
        "provider": "openai",
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    config = ProviderConfig.from_dict(config_dict)
    
    print(f"\nCreated config from dictionary:")
    print(f"  Provider: {config.provider}")
    print(f"  Model: {config.model}")
    print(f"  Temperature: {config.config.get('temperature')}")
    print(f"  Max tokens: {config.config.get('max_tokens')}")


def example_file_config():
    """Load configuration from JSON file"""
    print("\n" + "=" * 60)
    print("File Configuration (JSON)")
    print("=" * 60)
    
    # Create example config file
    config_data = {
        "providers": {
            "openai": {
                "provider": "openai",
                "model": "gpt-4",
                "temperature": 0.7
            },
            "anthropic": {
                "provider": "anthropic",
                "model": "claude-3-opus-20240229"
            }
        },
        "default_provider": "openai"
    }
    
    config_file = Path("example_config.json")
    
    try:
        # Write example config
        with open(config_file, "w") as f:
            json.dump(config_data, f, indent=2)
        
        print(f"\nCreated example config file: {config_file}")
        
        # Load config
        manager = LLMProviderConfig.from_file(str(config_file))
        
        print(f"\nLoaded configuration:")
        print(f"  Default provider: {manager.default_provider}")
        print(f"  Available providers: {list(manager.providers.keys())}")
        
        # Get provider config
        openai_config = manager.get_provider("openai")
        if openai_config:
            print(f"\nOpenAI config:")
            print(f"  Model: {openai_config.model}")
            print(f"  Temperature: {openai_config.config.get('temperature')}")
        
        # Create provider from config
        if openai_config:
            # Extract config, excluding provider/model (already passed separately)
            config_dict = {k: v for k, v in openai_config.config.items() 
                          if k not in ['provider', 'provider_name', 'model']}
            provider = create_provider(
                openai_config.provider,
                model=openai_config.model,
                **config_dict
            )
            print(f"\nCreated provider: {provider}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up example file
        if config_file.exists():
            config_file.unlink()
            print(f"\nCleaned up example config file")


def example_multi_provider_config():
    """Example with multiple providers"""
    print("\n" + "=" * 60)
    print("Multi-Provider Configuration")
    print("=" * 60)
    
    manager = LLMProviderConfig()
    
    # Add multiple providers
    manager.add_provider(
        "openai",
        ProviderConfig(provider="openai", model="gpt-4")
    )
    manager.add_provider(
        "anthropic",
        ProviderConfig(provider="anthropic", model="claude-3-opus-20240229")
    )
    manager.add_provider(
        "ollama",
        ProviderConfig(provider="ollama", model="llama2", base_url="http://localhost:11434")
    )
    
    manager.set_default("openai")
    
    print(f"\nConfigured {len(manager.providers)} providers:")
    for name, config in manager.providers.items():
        print(f"  - {name}: {config.model}")
    
    print(f"\nDefault provider: {manager.default_provider}")
    
    # Convert to dict
    config_dict = manager.to_dict()
    print(f"\nConfig as dictionary:")
    print(json.dumps(config_dict, indent=2))


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("LLM Provider - Configuration Examples")
    print("=" * 60)
    
    example_env_config()
    example_dict_config()
    example_file_config()
    example_multi_provider_config()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
