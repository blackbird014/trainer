#!/usr/bin/env python3
"""
Cloud Providers Examples

Demonstrates using cloud-based LLM providers (AWS, Google, Azure).
"""

import os
from llm_provider import (
    AWSBedrockProvider,
    GoogleVertexProvider,
    AzureOpenAIProvider,
    AWSSageMakerProvider
)


def aws_bedrock_example():
    """Example using AWS Bedrock"""
    print("=" * 60)
    print("AWS Bedrock Example")
    print("=" * 60)
    
    try:
        # Initialize Bedrock provider
        provider = AWSBedrockProvider(
            model="anthropic.claude-3-opus-20240229-v1:0",
            region="us-east-1"
            # Uses AWS credentials from environment or boto3 config
        )
        
        print("\nProvider initialized:")
        print(f"  Provider: {provider.provider_name}")
        print(f"  Model: {provider.model}")
        print(f"  Region: {provider.config.get('aws_region_name')}")
        
        # List available models (if boto3 is available)
        try:
            models = provider.list_models()
            print(f"\nAvailable models: {len(models)} found")
            if models:
                print(f"  Sample: {models[0]}")
        except Exception as e:
            print(f"\nCould not list models: {e}")
        
        # Complete prompt
        print("\nCompleting prompt...")
        result = provider.complete("What is AWS Bedrock?")
        
        print(f"\nResponse: {result.content}")
        print(f"Tokens: {result.tokens_used}, Cost: ${result.cost:.4f}")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nNote: Make sure you have:")
        print("  1. AWS credentials configured (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)")
        print("  2. Appropriate IAM permissions for Bedrock")
        print("  3. boto3 installed: pip install boto3")


def google_vertex_example():
    """Example using Google Vertex AI"""
    print("\n" + "=" * 60)
    print("Google Vertex AI Example")
    print("=" * 60)
    
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    
    if not project_id:
        print("\nSkipping: GOOGLE_CLOUD_PROJECT not set")
        return
    
    try:
        # Initialize Vertex AI provider
        provider = GoogleVertexProvider(
            model="gemini-pro",
            project_id=project_id,
            location="us-central1"
            # Uses Google Cloud credentials from environment
        )
        
        print("\nProvider initialized:")
        print(f"  Provider: {provider.provider_name}")
        print(f"  Model: {provider.model}")
        print(f"  Project: {provider.config.get('vertex_project')}")
        print(f"  Location: {provider.config.get('vertex_location')}")
        
        # Complete prompt
        print("\nCompleting prompt...")
        result = provider.complete("What is Google Vertex AI?")
        
        print(f"\nResponse: {result.content}")
        print(f"Tokens: {result.tokens_used}, Cost: ${result.cost:.4f}")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nNote: Make sure you have:")
        print("  1. Google Cloud project ID set")
        print("  2. GOOGLE_APPLICATION_CREDENTIALS set or default credentials")
        print("  3. google-cloud-aiplatform installed: pip install google-cloud-aiplatform")


def azure_openai_example():
    """Example using Azure OpenAI"""
    print("\n" + "=" * 60)
    print("Azure OpenAI Example")
    print("=" * 60)
    
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
    
    if not endpoint or not api_key:
        print("\nSkipping: AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_API_KEY not set")
        return
    
    try:
        # Initialize Azure OpenAI provider
        provider = AzureOpenAIProvider(
            model="gpt-4",
            endpoint=endpoint,
            api_key=api_key,
            api_version="2024-02-15-preview"
        )
        
        print("\nProvider initialized:")
        print(f"  Provider: {provider.provider_name}")
        print(f"  Model: {provider.model}")
        print(f"  Endpoint: {provider.config.get('api_base')}")
        print(f"  API Version: {provider.config.get('api_version')}")
        
        # Complete prompt
        print("\nCompleting prompt...")
        result = provider.complete("What is Azure OpenAI?")
        
        print(f"\nResponse: {result.content}")
        print(f"Tokens: {result.tokens_used}, Cost: ${result.cost:.4f}")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nNote: Make sure you have:")
        print("  1. Azure OpenAI endpoint URL")
        print("  2. Azure OpenAI API key")
        print("  3. Appropriate Azure subscription and resource")


def aws_sagemaker_example():
    """Example using AWS SageMaker"""
    print("\n" + "=" * 60)
    print("AWS SageMaker Example")
    print("=" * 60)
    
    endpoint_name = os.getenv("SAGEMAKER_ENDPOINT_NAME", "")
    
    if not endpoint_name:
        print("\nSkipping: SAGEMAKER_ENDPOINT_NAME not set")
        return
    
    try:
        # Initialize SageMaker provider
        provider = AWSSageMakerProvider(
            endpoint_name=endpoint_name,
            region="us-east-1"
            # Uses AWS credentials from environment
        )
        
        print("\nProvider initialized:")
        print(f"  Provider: {provider.provider_name}")
        print(f"  Endpoint: {provider.endpoint_name}")
        print(f"  Region: {provider.region}")
        
        # Complete prompt
        print("\nCompleting prompt...")
        result = provider.complete("Test prompt")
        
        print(f"\nResponse: {result.content}")
        print(f"Tokens: {result.tokens_used}")
        print(f"Note: SageMaker cost calculation not implemented")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nNote: Make sure you have:")
        print("  1. SageMaker endpoint deployed")
        print("  2. AWS credentials configured")
        print("  3. boto3 installed: pip install boto3")
        print("  4. Appropriate IAM permissions")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("LLM Provider - Cloud Providers Examples")
    print("=" * 60)
    
    print("\nNote: These examples require cloud provider credentials.")
    print("Set appropriate environment variables before running.\n")
    
    try:
        aws_bedrock_example()
        google_vertex_example()
        azure_openai_example()
        aws_sagemaker_example()
        
        print("\n" + "=" * 60)
        print("Examples completed!")
        print("=" * 60)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

