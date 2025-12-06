"""
Tests for LiteLLM wrapper
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from llm_provider import LiteLLMProvider, CompletionResult


class TestLiteLLMProvider:
    """Tests for LiteLLMProvider wrapper"""
    
    @patch('llm_provider.litellm_wrapper.completion')
    @patch('llm_provider.litellm_wrapper.completion_cost')
    def test_complete_success(self, mock_cost, mock_completion):
        """Test successful completion"""
        # Mock LiteLLM response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 20
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 10
        mock_response.id = "test-id"
        mock_response.model = "gpt-4"
        mock_response.created = 1234567890
        
        mock_completion.return_value = mock_response
        mock_cost.return_value = 0.002
        
        provider = LiteLLMProvider("openai", "gpt-4")
        result = provider.complete("test prompt")
        
        assert isinstance(result, CompletionResult)
        assert result.content == "Test response"
        assert result.tokens_used == 20
        assert result.model == "gpt-4"
        assert result.provider == "openai"
        assert result.cost == 0.002
        
        # Verify LiteLLM was called correctly
        mock_completion.assert_called_once()
        call_kwargs = mock_completion.call_args
        assert call_kwargs[1]["model"] == "openai/gpt-4"
        assert call_kwargs[1]["messages"] == [{"role": "user", "content": "test prompt"}]
    
    @patch('llm_provider.litellm_wrapper.completion')
    def test_complete_with_kwargs(self, mock_completion):
        """Test completion with additional kwargs"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 10
        mock_response.usage.prompt_tokens = 5
        mock_response.usage.completion_tokens = 5
        mock_response.id = "test-id"
        mock_response.model = "gpt-4"
        
        mock_completion.return_value = mock_response
        
        provider = LiteLLMProvider("openai", "gpt-4", temperature=0.7)
        result = provider.complete("test", max_tokens=100)
        
        # Verify kwargs were passed
        call_kwargs = mock_completion.call_args[1]
        assert call_kwargs["temperature"] == 0.7
        assert call_kwargs["max_tokens"] == 100
    
    @patch('llm_provider.litellm_wrapper.completion')
    def test_stream(self, mock_completion):
        """Test streaming completion"""
        # Mock stream chunks
        chunk1 = Mock()
        chunk1.choices = [Mock()]
        chunk1.choices[0].delta = Mock()
        chunk1.choices[0].delta.content = "Hello"
        
        chunk2 = Mock()
        chunk2.choices = [Mock()]
        chunk2.choices[0].delta = Mock()
        chunk2.choices[0].delta.content = " World"
        
        mock_completion.return_value = [chunk1, chunk2]
        
        provider = LiteLLMProvider("openai", "gpt-4")
        chunks = list(provider.stream("test"))
        
        assert chunks == ["Hello", " World"]
        # Verify stream=True was passed
        call_kwargs = mock_completion.call_args[1]
        assert call_kwargs.get("stream") is True
    
    @patch('llm_provider.litellm_wrapper.completion_cost')
    def test_get_cost(self, mock_cost):
        """Test cost calculation"""
        mock_cost.return_value = 0.001
        
        provider = LiteLLMProvider("openai", "gpt-4")
        cost = provider.get_cost(1000)
        
        assert cost == 0.001
        mock_cost.assert_called_once()
    
    @patch('llm_provider.litellm_wrapper.completion_cost')
    def test_get_cost_returns_zero_on_error(self, mock_cost):
        """Test that get_cost returns 0.0 on error"""
        mock_cost.side_effect = Exception("Cost calculation failed")
        
        provider = LiteLLMProvider("openai", "gpt-4")
        cost = provider.get_cost(1000)
        
        assert cost == 0.0
    
    @patch('llm_provider.litellm_wrapper.completion')
    def test_complete_handles_missing_usage(self, mock_completion):
        """Test completion when usage is missing"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = None
        mock_response.id = "test-id"
        mock_response.model = "gpt-4"
        
        mock_completion.return_value = mock_response
        
        provider = LiteLLMProvider("openai", "gpt-4")
        result = provider.complete("test")
        
        assert result.tokens_used == 0
        assert result.cost == 0.0
