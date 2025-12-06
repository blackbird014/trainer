"""
AWS SageMaker Provider

Direct implementation for AWS SageMaker endpoints.
Useful for custom fine-tuned models or proprietary models deployed on SageMaker.
"""

import json
import logging
from typing import Dict, Any, Optional, Iterator
from datetime import datetime

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

from ...base import LLMProvider, CompletionResult

logger = logging.getLogger(__name__)


class AWSSageMakerProvider(LLMProvider):
    """
    AWS SageMaker provider - direct implementation.
    
    Supports custom SageMaker endpoints with custom inference logic.
    Useful for fine-tuned models or proprietary models.
    """
    
    def __init__(
        self,
        endpoint_name: str,
        region: str = "us-east-1",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize AWS SageMaker provider.
        
        Args:
            endpoint_name: SageMaker endpoint name
            region: AWS region (default: "us-east-1")
            aws_access_key_id: AWS access key ID (optional)
            aws_secret_access_key: AWS secret access key (optional)
            **kwargs: Additional configuration
        """
        if not BOTO3_AVAILABLE:
            raise ImportError(
                "boto3 is required for AWSSageMakerProvider. "
                "Install it with: pip install boto3"
            )
        
        super().__init__(
            provider_name="sagemaker",
            model=endpoint_name,
            **kwargs
        )
        
        self.endpoint_name = endpoint_name
        self.region = region
        
        # Initialize SageMaker runtime client
        client_kwargs = {"region_name": region}
        if aws_access_key_id and aws_secret_access_key:
            client_kwargs["aws_access_key_id"] = aws_access_key_id
            client_kwargs["aws_secret_access_key"] = aws_secret_access_key
        
        self.client = boto3.client('sagemaker-runtime', **client_kwargs)
    
    def complete(self, prompt: str, **kwargs) -> CompletionResult:
        """
        Complete a prompt using SageMaker endpoint.
        
        Args:
            prompt: The prompt text to complete
            **kwargs: Additional parameters (content_type, accept, etc.)
            
        Returns:
            CompletionResult with the generated content and metadata
        """
        try:
            # Prepare request payload
            # Most SageMaker endpoints expect JSON with "inputs" key
            payload = kwargs.get("payload", {"inputs": prompt})
            if isinstance(payload, dict):
                body = json.dumps(payload).encode('utf-8')
            else:
                body = payload if isinstance(payload, bytes) else str(payload).encode('utf-8')
            
            # Invoke endpoint
            content_type = kwargs.get("content_type", "application/json")
            accept = kwargs.get("accept", "application/json")
            
            response = self.client.invoke_endpoint(
                EndpointName=self.endpoint_name,
                ContentType=content_type,
                Accept=accept,
                Body=body
            )
            
            # Parse response
            response_body = response['Body'].read()
            
            if accept == "application/json":
                result = json.loads(response_body)
                # Extract content (format depends on model)
                content = self._extract_content(result)
            else:
                content = response_body.decode('utf-8')
            
            # Estimate tokens (SageMaker doesn't provide token counts)
            tokens_used = self._estimate_tokens(prompt, content)
            
            # Calculate cost (SageMaker pricing varies, return 0 for now)
            cost = 0.0
            
            # Build metadata
            metadata = {
                "endpoint_name": self.endpoint_name,
                "region": self.region,
                "content_type": content_type,
                "accept": accept,
                "response_metadata": response.get("ResponseMetadata", {})
            }
            
            return CompletionResult(
                content=content,
                tokens_used=tokens_used,
                model=self.endpoint_name,
                provider="sagemaker",
                cost=cost,
                metadata=metadata
            )
        
        except ClientError as e:
            logger.error(
                f"Error invoking SageMaker endpoint {self.endpoint_name}",
                extra={"error": str(e), "endpoint": self.endpoint_name}
            )
            raise RuntimeError(f"SageMaker invocation failed: {e}") from e
        except Exception as e:
            logger.error(
                f"Unexpected error with SageMaker endpoint {self.endpoint_name}",
                extra={"error": str(e), "endpoint": self.endpoint_name}
            )
            raise
    
    def stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """
        Stream a completion from SageMaker endpoint.
        
        Note: Not all SageMaker endpoints support streaming.
        This is a basic implementation that may need customization.
        
        Args:
            prompt: The prompt text to complete
            **kwargs: Additional parameters
            
        Yields:
            str: Chunks of the generated content
        """
        # For now, get full completion and yield it as a single chunk
        # Custom implementations can override this for true streaming
        result = self.complete(prompt, **kwargs)
        yield result.content
    
    def get_cost(self, tokens: int) -> float:
        """
        Calculate cost for SageMaker endpoint.
        
        Note: SageMaker pricing varies by instance type and model.
        This returns 0.0 as a placeholder - implement based on your pricing.
        
        Args:
            tokens: Number of tokens
            
        Returns:
            Cost in USD (0.0 as placeholder)
        """
        # SageMaker pricing is complex and depends on instance type
        # Return 0.0 as placeholder - implement based on your specific setup
        return 0.0
    
    def _extract_content(self, result: Dict[str, Any]) -> str:
        """
        Extract content from SageMaker response.
        
        Different models return different formats, so this tries common patterns.
        
        Args:
            result: Parsed JSON response
            
        Returns:
            Extracted content string
        """
        # Try common response formats
        if isinstance(result, str):
            return result
        
        if isinstance(result, dict):
            # Try common keys
            for key in ["generated_text", "output", "completion", "text", "content"]:
                if key in result:
                    value = result[key]
                    if isinstance(value, str):
                        return value
                    if isinstance(value, list) and len(value) > 0:
                        if isinstance(value[0], dict) and "generated_text" in value[0]:
                            return value[0]["generated_text"]
                        return str(value[0])
            
            # If it's a list in the dict
            if "outputs" in result and isinstance(result["outputs"], list):
                return str(result["outputs"][0])
        
        # Fallback: return string representation
        return str(result)
    
    def _estimate_tokens(self, prompt: str, completion: str) -> int:
        """
        Estimate token count (rough approximation).
        
        Args:
            prompt: Prompt text
            completion: Completion text
            
        Returns:
            Estimated token count
        """
        # Rough estimation: ~4 characters per token
        total_chars = len(prompt) + len(completion)
        return total_chars // 4

