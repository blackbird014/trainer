#!/usr/bin/env python3
"""
Basic Usage Examples

Demonstrates basic usage of the LLM Provider module.
"""

from llm_provider import OpenAIProvider, CompletionResult


def basic_completion():
    """Basic completion example"""
    print("=" * 60)
    print("Basic Completion Example")
    print("=" * 60)
    
    # Create provider
    provider = OpenAIProvider(model="gpt-4")
    
    # Complete a prompt
    result = provider.complete("What is the capital of France?")
    
    print(f"\nPrompt: What is the capital of France?")
    print(f"\nResponse: {result.content}")
    print(f"\nMetadata:")
    print(f"  - Tokens used: {result.tokens_used}")
    print(f"  - Cost: ${result.cost:.4f}")
    print(f"  - Model: {result.model}")
    print(f"  - Provider: {result.provider}")


def streaming_example():
    """Streaming completion example"""
    print("\n" + "=" * 60)
    print("Streaming Example")
    print("=" * 60)
    
    provider = OpenAIProvider(model="gpt-4")
    
    print("\nPrompt: Write a short poem about Python")
    print("\nResponse (streaming):")
    print("-" * 60)
    
    for chunk in provider.stream("Write a short poem about Python"):
        print(chunk, end="", flush=True)
    
    print("\n" + "-" * 60)


def with_parameters():
    """Example with custom parameters"""
    print("\n" + "=" * 60)
    print("Custom Parameters Example")
    print("=" * 60)
    
    provider = OpenAIProvider(model="gpt-4")
    
    result = provider.complete(
        "Write a haiku about coding",
        temperature=0.9,
        max_tokens=50
    )
    
    print(f"\nPrompt: Write a haiku about coding")
    print(f"Parameters: temperature=0.9, max_tokens=50")
    print(f"\nResponse: {result.content}")


def cost_calculation():
    """Cost calculation example"""
    print("\n" + "=" * 60)
    print("Cost Calculation Example")
    print("=" * 60)
    
    provider = OpenAIProvider(model="gpt-4")
    
    # Calculate cost for different token counts
    token_counts = [100, 500, 1000, 5000]
    
    print("\nToken Cost Estimates:")
    for tokens in token_counts:
        cost = provider.get_cost(tokens)
        print(f"  {tokens:5d} tokens = ${cost:.4f}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("LLM Provider - Basic Usage Examples")
    print("=" * 60)
    
    try:
        basic_completion()
        streaming_example()
        with_parameters()
        cost_calculation()
        
        print("\n" + "=" * 60)
        print("Examples completed!")
        print("=" * 60)
    except Exception as e:
        print(f"\nError: {e}")
        print("\nNote: Make sure you have:")
        print("  1. Set OPENAI_API_KEY environment variable")
        print("  2. Installed required dependencies")
        print("  3. Have internet connection")

