#!/usr/bin/env python3
"""
All Providers Example

Demonstrates usage of all available LLM providers.
"""

import os
from llm_provider import (
    OpenAIProvider,
    AnthropicProvider,
    OllamaProvider,
    AWSBedrockProvider,
    GoogleVertexProvider,
    AzureOpenAIProvider,
    HuggingFaceProvider,
    AWSSageMakerProvider
)


def example_openai():
    """OpenAI provider example"""
    print("\n" + "=" * 60)
    print("OpenAI Provider")
    print("=" * 60)
    
    try:
        provider = OpenAIProvider(model="gpt-4")
        result = provider.complete("Hello from OpenAI!")
        print(f"Response: {result.content[:100]}...")
        print(f"Tokens: {result.tokens_used}, Cost: ${result.cost:.4f}")
    except Exception as e:
        print(f"Error: {e}")
        print("Note: Set OPENAI_API_KEY environment variable")


def example_anthropic():
    """Anthropic provider example"""
    print("\n" + "=" * 60)
    print("Anthropic Provider")
    print("=" * 60)
    
    try:
        provider = AnthropicProvider(model="claude-3-opus-20240229")
        result = provider.complete("Hello from Anthropic!")
        print(f"Response: {result.content[:100]}...")
        print(f"Tokens: {result.tokens_used}, Cost: ${result.cost:.4f}")
    except Exception as e:
        print(f"Error: {e}")
        print("Note: Set ANTHROPIC_API_KEY environment variable")


def example_ollama():
    """Ollama provider example"""
    print("\n" + "=" * 60)
    print("Ollama Provider (Local)")
    print("=" * 60)
    
    try:
        provider = OllamaProvider(model="llama2", base_url="http://localhost:11434")
        result = provider.complete("Hello from Ollama!")
        print(f"Response: {result.content[:100]}...")
        print(f"Tokens: {result.tokens_used}")
    except Exception as e:
        print(f"Error: {e}")
        print("Note: Make sure Ollama is running locally on port 11434")


def example_bedrock():
    """AWS Bedrock provider example"""
    print("\n" + "=" * 60)
    print("AWS Bedrock Provider")
    print("=" * 60)
    
    try:
        provider = AWSBedrockProvider(
            model="anthropic.claude-3-opus-20240229-v1:0",
            region="us-east-1"
        )
        result = provider.complete("Hello from Bedrock!")
        print(f"Response: {result.content[:100]}...")
        print(f"Tokens: {result.tokens_used}, Cost: ${result.cost:.4f}")
    except Exception as e:
        print(f"Error: {e}")
        print("Note: Configure AWS credentials and ensure Bedrock access")


def example_vertex():
    """Google Vertex AI provider example"""
    print("\n" + "=" * 60)
    print("Google Vertex AI Provider")
    print("=" * 60)
    
    try:
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id")
        provider = GoogleVertexProvider(
            model="gemini-pro",
            project_id=project_id,
            location="us-central1"
        )
        result = provider.complete("Hello from Vertex AI!")
        print(f"Response: {result.content[:100]}...")
        print(f"Tokens: {result.tokens_used}, Cost: ${result.cost:.4f}")
    except Exception as e:
        print(f"Error: {e}")
        print("Note: Set GOOGLE_APPLICATION_CREDENTIALS and GOOGLE_CLOUD_PROJECT")


def example_azure():
    """Azure OpenAI provider example"""
    print("\n" + "=" * 60)
    print("Azure OpenAI Provider")
    print("=" * 60)
    
    try:
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://your-resource.openai.azure.com/")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        
        provider = AzureOpenAIProvider(
            model="gpt-4",
            endpoint=endpoint,
            api_key=api_key
        )
        result = provider.complete("Hello from Azure!")
        print(f"Response: {result.content[:100]}...")
        print(f"Tokens: {result.tokens_used}, Cost: ${result.cost:.4f}")
    except Exception as e:
        print(f"Error: {e}")
        print("Note: Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY")


def example_huggingface():
    """HuggingFace provider example"""
    print("\n" + "=" * 60)
    print("HuggingFace Provider")
    print("=" * 60)
    
    try:
        provider = HuggingFaceProvider(
            model="meta-llama/Llama-2-7b-chat-hf"
        )
        result = provider.complete("Hello from HuggingFace!")
        print(f"Response: {result.content[:100]}...")
        print(f"Tokens: {result.tokens_used}, Cost: ${result.cost:.4f}")
    except Exception as e:
        print(f"Error: {e}")
        print("Note: Set HUGGINGFACE_API_KEY environment variable")


def example_sagemaker():
    """AWS SageMaker provider example"""
    print("\n" + "=" * 60)
    print("AWS SageMaker Provider")
    print("=" * 60)
    
    try:
        provider = AWSSageMakerProvider(
            endpoint_name="your-endpoint-name",
            region="us-east-1"
        )
        result = provider.complete("Hello from SageMaker!")
        print(f"Response: {result.content[:100]}...")
        print(f"Tokens: {result.tokens_used}")
    except Exception as e:
        print(f"Error: {e}")
        print("Note: Configure AWS credentials and provide valid endpoint name")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("LLM Provider - All Providers Examples")
    print("=" * 60)
    print("\nNote: These examples require API keys/credentials for each provider.")
    print("Most will fail without proper configuration - this is expected.\n")
    
    example_openai()
    example_anthropic()
    example_ollama()
    example_bedrock()
    example_vertex()
    example_azure()
    example_huggingface()
    example_sagemaker()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)

