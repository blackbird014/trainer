"""
AWS Bedrock Provider

AWS Bedrock provider implementation via LiteLLM.
Supports Claude, Llama, Titan, and other Bedrock models.
"""

from typing import Optional
from ...litellm_wrapper import LiteLLMProvider


class AWSBedrockProvider(LiteLLMProvider):
    """
    AWS Bedrock provider via LiteLLM.
    
    Supports Claude, Llama, Titan, and other Bedrock foundation models.
    Authentication via AWS credentials (IAM, environment variables, or boto3 config).
    """
    
    def __init__(
        self,
        model: str,
        region: str = "us-east-1",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize AWS Bedrock provider.
        
        Args:
            model: Bedrock model ID (e.g., "anthropic.claude-3-opus-20240229-v1:0")
            region: AWS region (default: "us-east-1")
            aws_access_key_id: AWS access key ID (optional, uses default credentials if not provided)
            aws_secret_access_key: AWS secret access key (optional)
            **kwargs: Additional LiteLLM configuration
        """
        # Set AWS credentials if provided
        if aws_access_key_id:
            kwargs["aws_access_key_id"] = aws_access_key_id
        if aws_secret_access_key:
            kwargs["aws_secret_access_key"] = aws_secret_access_key
        
        # Set region
        kwargs["aws_region_name"] = region
        
        super().__init__(
            provider="bedrock",
            model=model,
            **kwargs
        )
    
    def list_models(self) -> list:
        """
        List available Bedrock models.
        
        Note: This requires boto3 and AWS credentials.
        """
        try:
            import boto3
            bedrock = boto3.client('bedrock', region_name=self.config.get("aws_region_name", "us-east-1"))
            response = bedrock.list_foundation_models()
            return [model["modelId"] for model in response.get("modelSummaries", [])]
        except ImportError:
            raise NotImplementedError("boto3 is required to list Bedrock models")
        except Exception as e:
            raise RuntimeError(f"Failed to list Bedrock models: {e}")

