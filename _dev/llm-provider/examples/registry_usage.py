#!/usr/bin/env python3
"""
Registry Usage Example

Demonstrates using the provider registry to create and manage providers.
"""

from llm_provider import (
    get_registry,
    create_provider,
    list_providers,
    register_provider,
    LLMProvider,
    CompletionResult
)


def example_list_providers():
    """List all registered providers"""
    print("=" * 60)
    print("Registered Providers")
    print("=" * 60)
    
    providers = list_providers()
    print(f"\nFound {len(providers)} registered providers:")
    for provider_name in providers:
        print(f"  - {provider_name}")


def example_create_from_registry():
    """Create provider using registry"""
    print("\n" + "=" * 60)
    print("Creating Provider from Registry")
    print("=" * 60)
    
    try:
        # Create OpenAI provider using registry
        provider = create_provider("openai", model="gpt-4")
        print(f"\nCreated provider: {provider}")
        print(f"Provider name: {provider.provider_name}")
        print(f"Model: {provider.model}")
        
        # You can use it like any other provider
        # result = provider.complete("Hello!")
        # print(f"Response: {result.content}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Note: This requires OPENAI_API_KEY to actually make requests")


def example_custom_provider():
    """Register and use a custom provider"""
    print("\n" + "=" * 60)
    print("Custom Provider Registration")
    print("=" * 60)
    
    # Define a custom provider
    class CustomTestProvider(LLMProvider):
        def complete(self, prompt: str, **kwargs) -> CompletionResult:
            return CompletionResult(
                content=f"Custom response to: {prompt}",
                tokens_used=len(prompt) // 4,
                model=self.model,
                provider=self.provider_name,
                cost=0.0
            )
        
        def stream(self, prompt: str, **kwargs):
            yield f"Custom streaming response to: {prompt}"
        
        def get_cost(self, tokens: int) -> float:
            return tokens * 0.00001
    
    # Register the custom provider
    register_provider("custom_test", CustomTestProvider)
    print("\nRegistered custom provider: custom_test")
    
    # Create and use it
    custom_provider = create_provider("custom_test", model="custom-model")
    result = custom_provider.complete("Hello from custom provider!")
    
    print(f"\nCustom provider response: {result.content}")
    print(f"Provider: {result.provider}, Model: {result.model}")


def example_registry_info():
    """Get registry information"""
    print("\n" + "=" * 60)
    print("Registry Information")
    print("=" * 60)
    
    registry = get_registry()
    
    print(f"\nDefault provider: {registry.get_default()}")
    print(f"Total providers: {len(registry.list_providers())}")
    
    # Show all providers
    print("\nAll registered providers:")
    for provider_name in registry.list_providers():
        print(f"  - {provider_name}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("LLM Provider - Registry Usage Examples")
    print("=" * 60)
    
    example_list_providers()
    example_create_from_registry()
    example_custom_provider()
    example_registry_info()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)

