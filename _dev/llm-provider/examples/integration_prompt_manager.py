#!/usr/bin/env python3
"""
Integration with Prompt Manager

Demonstrates using LLM Provider with Prompt Manager module.
"""

import sys
from pathlib import Path

# Add parent directories to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "prompt-manager" / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from prompt_manager import PromptManager, PromptTemplate
    from llm_provider import OpenAIProvider, create_provider, CompletionResult
    PROMPT_MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import prompt_manager: {e}")
    print("This example requires prompt-manager module to be installed")
    PROMPT_MANAGER_AVAILABLE = False


def example_prompt_manager_with_llm():
    """Use PromptManager to load prompts and LLM Provider to execute them"""
    if not PROMPT_MANAGER_AVAILABLE:
        print("Skipping: prompt-manager not available")
        return
    
    print("=" * 60)
    print("Prompt Manager + LLM Provider Integration")
    print("=" * 60)
    
    try:
        # Initialize PromptManager
        prompt_manager = PromptManager(
            context_dir=str(Path(__file__).parent.parent.parent.parent / "information" / "context"),
            cache_enabled=True
        )
        
        # Initialize LLM Provider
        llm_provider = OpenAIProvider(model="gpt-4")
        
        # Load a prompt template
        template = PromptTemplate("Analyze the following company: {company_name}")
        
        # Fill template with parameters
        filled_prompt = prompt_manager.fill_template(template, {"company_name": "Apple Inc."})
        
        print(f"\nFilled Prompt:")
        print(f"{filled_prompt}")
        
        # Execute with LLM Provider
        print(f"\nExecuting with LLM Provider...")
        result = llm_provider.complete(filled_prompt)
        
        print(f"\nLLM Response:")
        print(f"{result.content[:200]}...")
        print(f"\nMetadata:")
        print(f"  - Tokens: {result.tokens_used}")
        print(f"  - Cost: ${result.cost:.4f}")
        print(f"  - Model: {result.model}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: This requires:")
        print("  1. prompt-manager module installed")
        print("  2. OPENAI_API_KEY environment variable")
        print("  3. Valid context directory")


def example_context_loading_and_llm():
    """Load contexts and use with LLM Provider"""
    if not PROMPT_MANAGER_AVAILABLE:
        print("Skipping: prompt-manager not available")
        return
    
    print("\n" + "=" * 60)
    print("Context Loading + LLM Provider")
    print("=" * 60)
    
    try:
        prompt_manager = PromptManager(
            context_dir=str(Path(__file__).parent.parent.parent.parent / "information" / "context")
        )
        llm_provider = OpenAIProvider(model="gpt-4")
        
        # Load context files
        contexts = prompt_manager.load_contexts([
            "biotech/01-introduction.md",
            "biotech/molecular-biology-foundations.md"
        ])
        
        print(f"\nLoaded {len(contexts)} characters of context")
        
        # Create prompt with context
        user_prompt = "Based on the context provided, explain molecular biology basics."
        full_prompt = f"{contexts}\n\n{user_prompt}"
        
        print(f"\nExecuting prompt with context...")
        result = llm_provider.complete(full_prompt[:1000])  # Limit for demo
        
        print(f"\nResponse: {result.content[:200]}...")
        print(f"Tokens: {result.tokens_used}, Cost: ${result.cost:.4f}")
        
    except FileNotFoundError:
        print("Context files not found - this is expected if context directory doesn't exist")
    except Exception as e:
        print(f"Error: {e}")


def example_prompt_composition_with_llm():
    """Compose multiple prompts and execute with LLM"""
    if not PROMPT_MANAGER_AVAILABLE:
        print("Skipping: prompt-manager not available")
        return
    
    print("\n" + "=" * 60)
    print("Prompt Composition + LLM Provider")
    print("=" * 60)
    
    try:
        prompt_manager = PromptManager()
        llm_provider = OpenAIProvider(model="gpt-4")
        
        # Create multiple templates
        templates = [
            PromptTemplate("System: You are a helpful assistant."),
            PromptTemplate("User: {question}"),
            PromptTemplate("Instructions: Provide a concise answer.")
        ]
        
        # Compose prompts
        composed = prompt_manager.compose(templates, strategy="sequential")
        
        # Fill with parameters
        filled = prompt_manager.fill_template(
            PromptTemplate(composed),
            {"question": "What is Python?"}
        )
        
        print(f"\nComposed Prompt:")
        print(f"{filled[:300]}...")
        
        # Execute with LLM
        result = llm_provider.complete(filled)
        
        print(f"\nResponse: {result.content[:200]}...")
        
    except Exception as e:
        print(f"Error: {e}")


def example_provider_switching():
    """Switch between different LLM providers"""
    print("\n" + "=" * 60)
    print("Provider Switching Example")
    print("=" * 60)
    
    if not PROMPT_MANAGER_AVAILABLE:
        print("Skipping: prompt-manager not available")
        return
    
    try:
        prompt_manager = PromptManager()
        template = PromptTemplate("Explain: {topic}")
        filled = prompt_manager.fill_template(template, {"topic": "machine learning"})
        
        # Try different providers
        providers = [
            ("openai", OpenAIProvider(model="gpt-4")),
            # Add more providers as needed
        ]
        
        print(f"\nPrompt: {filled}")
        print(f"\nTrying {len(providers)} providers...")
        
        for provider_name, provider in providers:
            try:
                print(f"\n--- {provider_name.upper()} ---")
                result = provider.complete(filled)
                print(f"Response: {result.content[:150]}...")
                print(f"Tokens: {result.tokens_used}, Cost: ${result.cost:.4f}")
            except Exception as e:
                print(f"Error with {provider_name}: {e}")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("LLM Provider - Prompt Manager Integration Examples")
    print("=" * 60)
    
    if not PROMPT_MANAGER_AVAILABLE:
        print("\n⚠️  prompt-manager module not found")
        print("Install it or adjust Python path to run these examples")
    else:
        example_prompt_manager_with_llm()
        example_context_loading_and_llm()
        example_prompt_composition_with_llm()
        example_provider_switching()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
