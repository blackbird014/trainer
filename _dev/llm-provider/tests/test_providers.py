"""
Tests for provider implementations
"""

import pytest
from unittest.mock import Mock, patch
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


class TestOpenAIProvider:
    """Tests for OpenAIProvider"""
    
    def test_initialization(self):
        """Test OpenAIProvider initialization"""
        provider = OpenAIProvider(model="gpt-4")
        
        assert provider.provider == "openai"
        assert provider.model == "gpt-4"
        assert provider.litellm_model == "openai/gpt-4"
    
    def test_initialization_with_api_key(self):
        """Test initialization with API key"""
        provider = OpenAIProvider(model="gpt-4", api_key="test-key")
        
        assert provider.litellm_config.get("api_key") == "test-key"
    
    @patch('llm_provider.litellm_wrapper.completion')
    def test_complete(self, mock_completion):
        """Test OpenAI completion"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "OpenAI response"
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 10
        mock_response.usage.prompt_tokens = 5
        mock_response.usage.completion_tokens = 5
        mock_response.id = "test-id"
        mock_response.model = "gpt-4"
        
        mock_completion.return_value = mock_response
        
        provider = OpenAIProvider(model="gpt-4")
        result = provider.complete("test")
        
        assert result.content == "OpenAI response"
        assert result.provider == "openai"


class TestAnthropicProvider:
    """Tests for AnthropicProvider"""
    
    def test_initialization(self):
        """Test AnthropicProvider initialization"""
        provider = AnthropicProvider(model="claude-3-opus-20240229")
        
        assert provider.provider == "anthropic"
        assert provider.model == "claude-3-opus-20240229"
        assert provider.litellm_model == "anthropic/claude-3-opus-20240229"


class TestOllamaProvider:
    """Tests for OllamaProvider"""
    
    def test_initialization_default(self):
        """Test OllamaProvider with default base URL"""
        provider = OllamaProvider(model="llama2")
        
        assert provider.provider == "ollama"
        assert provider.model == "llama2"
        assert provider.litellm_config.get("api_base") == "http://localhost:11434"
    
    def test_initialization_custom_url(self):
        """Test OllamaProvider with custom base URL"""
        provider = OllamaProvider(model="llama2", base_url="http://custom:8080")
        
        assert provider.litellm_config.get("api_base") == "http://custom:8080"


class TestAWSBedrockProvider:
    """Tests for AWSBedrockProvider"""
    
    def test_initialization(self):
        """Test AWSBedrockProvider initialization"""
        provider = AWSBedrockProvider(
            model="anthropic.claude-3-opus-20240229-v1:0",
            region="us-west-2"
        )
        
        assert provider.provider == "bedrock"
        assert provider.config.get("aws_region_name") == "us-west-2"
    
    def test_initialization_with_credentials(self):
        """Test initialization with AWS credentials"""
        provider = AWSBedrockProvider(
            model="test-model",
            aws_access_key_id="test-key",
            aws_secret_access_key="test-secret"
        )
        
        assert provider.config.get("aws_access_key_id") == "test-key"
        assert provider.config.get("aws_secret_access_key") == "test-secret"
    
    @pytest.mark.skipif(True, reason="boto3 not installed in test environment")
    @patch('boto3.client')
    def test_list_models(self, mock_boto3):
        """Test listing Bedrock models"""
        mock_client = Mock()
        mock_client.list_foundation_models.return_value = {
            "modelSummaries": [
                {"modelId": "model1"},
                {"modelId": "model2"}
            ]
        }
        mock_boto3.return_value = mock_client
        
        provider = AWSBedrockProvider(model="test", region="us-east-1")
        models = provider.list_models()
        
        assert models == ["model1", "model2"]


class TestGoogleVertexProvider:
    """Tests for GoogleVertexProvider"""
    
    def test_initialization(self):
        """Test GoogleVertexProvider initialization"""
        provider = GoogleVertexProvider(
            model="gemini-pro",
            project_id="test-project",
            location="us-central1"
        )
        
        assert provider.provider == "vertex_ai"
        assert provider.config.get("vertex_project") == "test-project"
        assert provider.config.get("vertex_location") == "us-central1"
    
    def test_initialization_with_credentials(self):
        """Test initialization with credentials path"""
        provider = GoogleVertexProvider(
            model="gemini-pro",
            project_id="test-project",
            credentials_path="/path/to/creds.json"
        )
        
        assert provider.config.get("vertex_credentials") == "/path/to/creds.json"


class TestAzureOpenAIProvider:
    """Tests for AzureOpenAIProvider"""
    
    def test_initialization(self):
        """Test AzureOpenAIProvider initialization"""
        provider = AzureOpenAIProvider(
            model="gpt-4",
            endpoint="https://test.openai.azure.com/",
            api_key="test-key"
        )
        
        assert provider.provider == "azure"
        assert provider.config.get("api_base") == "https://test.openai.azure.com/"
        assert provider.config.get("api_key") == "test-key"
        assert provider.config.get("api_version") == "2024-02-15-preview"


class TestHuggingFaceProvider:
    """Tests for HuggingFaceProvider"""
    
    def test_initialization(self):
        """Test HuggingFaceProvider initialization"""
        provider = HuggingFaceProvider(model="meta-llama/Llama-2-7b-chat-hf")
        
        assert provider.provider == "huggingface"
        assert provider.model == "meta-llama/Llama-2-7b-chat-hf"
    
    def test_initialization_with_api_key(self):
        """Test initialization with API key"""
        provider = HuggingFaceProvider(
            model="test-model",
            api_key="test-key"
        )
        
        assert provider.litellm_config.get("api_key") == "test-key"


class TestAWSSageMakerProvider:
    """Tests for AWSSageMakerProvider"""
    
    @pytest.mark.skipif(True, reason="boto3 not installed in test environment")
    @patch('boto3.client')
    def test_initialization(self, mock_boto3):
        """Test AWSSageMakerProvider initialization"""
        mock_boto3.return_value = Mock()
        
        provider = AWSSageMakerProvider(
            endpoint_name="test-endpoint",
            region="us-east-1"
        )
        
        assert provider.provider_name == "sagemaker"
        assert provider.endpoint_name == "test-endpoint"
        assert provider.region == "us-east-1"
        mock_boto3.assert_called_once()
    
    def test_initialization_without_boto3(self):
        """Test that initialization fails without boto3"""
        # Temporarily remove boto3
        import sys
        if 'boto3' in sys.modules:
            del sys.modules['boto3']
        
        with patch.dict('sys.modules', {'boto3': None}):
            with pytest.raises(ImportError, match="boto3 is required"):
                AWSSageMakerProvider(endpoint_name="test", region="us-east-1")
    
    @pytest.mark.skipif(True, reason="boto3 not installed in test environment")
    @patch('boto3.client')
    @patch('json.loads')
    def test_complete(self, mock_json, mock_boto3):
        """Test SageMaker completion"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response['Body'].read.return_value = b'{"generated_text": "SageMaker response"}'
        mock_client.invoke_endpoint.return_value = mock_response
        mock_boto3.return_value = mock_client
        mock_json.return_value = {"generated_text": "SageMaker response"}
        
        provider = AWSSageMakerProvider(endpoint_name="test", region="us-east-1")
        result = provider.complete("test prompt")
        
        assert result.content == "SageMaker response"
        assert result.provider == "sagemaker"
        mock_client.invoke_endpoint.assert_called_once()
