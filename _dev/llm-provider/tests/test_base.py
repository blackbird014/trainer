"""
Tests for base LLM provider abstraction
"""

import pytest
from datetime import datetime
from llm_provider import LLMProvider, CompletionResult


class MockProvider(LLMProvider):
    """Mock provider for testing"""
    
    def complete(self, prompt: str, **kwargs) -> CompletionResult:
        return CompletionResult(
            content=f"Response to: {prompt}",
            tokens_used=10,
            model=self.model,
            provider=self.provider_name,
            cost=0.001
        )
    
    def stream(self, prompt: str, **kwargs):
        yield "chunk1"
        yield "chunk2"
    
    def get_cost(self, tokens: int) -> float:
        return tokens * 0.0001


class TestCompletionResult:
    """Tests for CompletionResult dataclass"""
    
    def test_completion_result_creation(self):
        """Test creating a CompletionResult"""
        result = CompletionResult(
            content="Test response",
            tokens_used=10,
            model="test-model",
            provider="test-provider",
            cost=0.001
        )
        
        assert result.content == "Test response"
        assert result.tokens_used == 10
        assert result.model == "test-model"
        assert result.provider == "test-provider"
        assert result.cost == 0.001
        assert isinstance(result.created_at, datetime)
    
    def test_completion_result_validation(self):
        """Test CompletionResult validation"""
        # Should raise ValueError for negative tokens
        with pytest.raises(ValueError, match="tokens_used must be non-negative"):
            CompletionResult(
                content="test",
                tokens_used=-1,
                model="test",
                provider="test",
                cost=0.0
            )
        
        # Should raise ValueError for negative cost
        with pytest.raises(ValueError, match="cost must be non-negative"):
            CompletionResult(
                content="test",
                tokens_used=10,
                model="test",
                provider="test",
                cost=-0.001
            )
        
        # Should raise ValueError for empty content
        with pytest.raises(ValueError, match="content cannot be empty"):
            CompletionResult(
                content="",
                tokens_used=10,
                model="test",
                provider="test",
                cost=0.0
            )
    
    def test_completion_result_metadata(self):
        """Test CompletionResult with metadata"""
        metadata = {"key": "value", "number": 42}
        result = CompletionResult(
            content="test",
            tokens_used=10,
            model="test",
            provider="test",
            cost=0.0,
            metadata=metadata
        )
        
        assert result.metadata == metadata


class TestLLMProvider:
    """Tests for LLMProvider base class"""
    
    def test_provider_initialization(self):
        """Test provider initialization"""
        provider = MockProvider("test-provider", "test-model", key="value")
        
        assert provider.provider_name == "test-provider"
        assert provider.model == "test-model"
        assert provider.config == {"key": "value"}
    
    def test_provider_complete(self):
        """Test provider complete method"""
        provider = MockProvider("test", "test-model")
        result = provider.complete("test prompt")
        
        assert isinstance(result, CompletionResult)
        assert "test prompt" in result.content
        assert result.tokens_used == 10
        assert result.provider == "test"
    
    def test_provider_stream(self):
        """Test provider stream method"""
        provider = MockProvider("test", "test-model")
        chunks = list(provider.stream("test prompt"))
        
        assert len(chunks) == 2
        assert chunks[0] == "chunk1"
        assert chunks[1] == "chunk2"
    
    def test_provider_get_cost(self):
        """Test provider get_cost method"""
        provider = MockProvider("test", "test-model")
        cost = provider.get_cost(1000)
        
        assert cost == 0.1  # 1000 * 0.0001
    
    def test_provider_list_models_not_implemented(self):
        """Test that list_models raises NotImplementedError by default"""
        provider = MockProvider("test", "test-model")
        
        with pytest.raises(NotImplementedError):
            provider.list_models()
    
    def test_provider_deploy_model_not_implemented(self):
        """Test that deploy_model raises NotImplementedError by default"""
        provider = MockProvider("test", "test-model")
        
        with pytest.raises(NotImplementedError):
            provider.deploy_model("model_path")
    
    def test_provider_repr(self):
        """Test provider string representation"""
        provider = MockProvider("test-provider", "test-model")
        repr_str = repr(provider)
        
        assert "MockProvider" in repr_str
        assert "test-provider" in repr_str
        assert "test-model" in repr_str
