#!/usr/bin/env python3
"""
Multiple Providers Example

Demonstrates using different LLM providers.
"""

from llm_provider import (
    OpenAIProvider,
    AnthropicProvider,
    OllamaProvider,
    create_provider
)


def compare_providers():
    """Compare responses from different providers"""
    print("=" * 60)
    print("Multiple Providers Comparison")
    print("=" * 60)
    
    prompt = "Explain quantum computing in one sentence."
    
    providers = [
        ("OpenAI", OpenAIProvider(model="gpt-4")),
        ("Anthropic", AnthropicProvider(model="claude-3-opus-20240229")),
    ]
    
    # Add Ollama if available
    try:
        providers.append(("Ollama", OllamaProvider(model="llama2")))
    except Exception:
        print("\nNote: Ollama provider skipped (not available)")
    
    print(f"\nPrompt: {prompt}\n")
    
    for name, provider in providers:
        try:
            print(f"\n{'-' * 60}")
            print(f"{name} Response:")
            print(f"{'-' * 60}")
            
            result = provider.complete(prompt)
            print(f"{result.content}")
            print(f"\nTokens: {result.tokens_used}, Cost: ${result.cost:.4f}")
            
        except Exception as e:
            print(f"Error with {name}: {e}")


def provider_registry_example():
    """Example using provider registry"""
    print("\n" + "=" * 60)
    print("Provider Registry Example")
    print("=" * 60)
    
    from llm_provider import list_providers, create_provider
    
    # List available providers
    print("\nAvailable providers:")
    for provider_name in list_providers():
        print(f"  - {provider_name}")
    
    # Create provider using registry
    print("\nCreating provider via registry...")
    provider = create_provider("openai", model="gpt-4")
    
    result = provider.complete("Hello from registry!")
    print(f"\nResponse: {result.content}")


def fallback_provider():
    """Example of fallback between providers"""
    print("\n" + "=" * 60)
    print("Fallback Provider Example")
    print("=" * 60)
    
    providers = [
        OpenAIProvider(model="gpt-4"),
        AnthropicProvider(model="claude-3-opus-20240229"),
    ]
    
    prompt = "What is machine learning?"
    
    print(f"\nPrompt: {prompt}")
    print("\nTrying providers in order...\n")
    
    for i, provider in enumerate(providers, 1):
        try:
            print(f"Attempt {i}: {provider.provider_name}...")
            result = provider.complete(prompt)
            print(f"✓ Success!")
            print(f"\nResponse: {result.content}")
            print(f"Tokens: {result.tokens_used}, Cost: ${result.cost:.4f}")
            break
        except Exception as e:
            print(f"✗ Failed: {e}")
            if i < len(providers):
                print("Trying next provider...\n")
            else:
                print("\nAll providers failed!")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("LLM Provider - Multiple Providers Examples")
    print("=" * 60)
    
    try:
        compare_providers()
        provider_registry_example()
        fallback_provider()
        
        print("\n" + "=" * 60)
        print("Examples completed!")
        print("=" * 60)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

