"""
Tests for utility functions
"""

import pytest
from llm_provider import (
    estimate_tokens,
    format_prompt,
    validate_provider_config,
    merge_provider_configs,
    get_provider_info,
    calculate_total_cost,
    calculate_total_tokens,
    CompletionResult,
    LLMProvider
)


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
    
    def get_cost(self, tokens: int) -> float:
        return tokens * 0.0001


class TestEstimateTokens:
    """Tests for estimate_tokens function"""
    
    def test_estimate_tokens_basic(self):
        """Test basic token estimation"""
        text = "Hello world" * 10  # 110 characters
        tokens = estimate_tokens(text)
        
        # Should be approximately 110 / 4 = 27-28 tokens
        assert 20 <= tokens <= 35
    
    def test_estimate_tokens_gpt4(self):
        """Test token estimation for GPT-4"""
        text = "Hello world" * 10
        tokens_gpt4 = estimate_tokens(text, model="gpt-4")
        tokens_default = estimate_tokens(text)
        
        # GPT-4 uses ~3.5 chars per token, so should be higher
        assert tokens_gpt4 >= tokens_default


class TestFormatPrompt:
    """Tests for format_prompt function"""
    
    def test_format_prompt_simple(self):
        """Test simple prompt formatting"""
        prompt = format_prompt(user_prompt="Hello")
        
        assert "User: Hello" in prompt
    
    def test_format_prompt_with_system(self):
        """Test prompt formatting with system prompt"""
        prompt = format_prompt(
            system_prompt="You are a helpful assistant",
            user_prompt="Hello"
        )
        
        assert "System:" in prompt
        assert "You are a helpful assistant" in prompt
        assert "User:" in prompt
        assert "Hello" in prompt
    
    def test_format_prompt_with_messages(self):
        """Test prompt formatting with messages list"""
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"}
        ]
        
        prompt = format_prompt(messages=messages)
        
        assert "System:" in prompt
        assert "You are helpful" in prompt
        assert "User:" in prompt
        assert "Hello" in prompt
    
    def test_format_prompt_empty(self):
        """Test formatting empty prompt"""
        prompt = format_prompt()
        
        assert prompt == ""


class TestValidateProviderConfig:
    """Tests for validate_provider_config function"""
    
    def test_validate_valid_config(self):
        """Test validating valid config"""
        config = {
            "provider": "openai",
            "model": "gpt-4"
        }
        
        assert validate_provider_config(config) is True
    
    def test_validate_missing_provider(self):
        """Test validating config missing provider"""
        config = {"model": "gpt-4"}
        
        assert validate_provider_config(config) is False
    
    def test_validate_missing_model(self):
        """Test validating config missing model"""
        config = {"provider": "openai"}
        
        assert validate_provider_config(config) is False


class TestMergeProviderConfigs:
    """Tests for merge_provider_configs function"""
    
    def test_merge_configs(self):
        """Test merging two configs"""
        base = {"provider": "openai", "model": "gpt-4", "temperature": 0.7}
        override = {"temperature": 0.9, "max_tokens": 100}
        
        merged = merge_provider_configs(base, override)
        
        assert merged["provider"] == "openai"
        assert merged["model"] == "gpt-4"
        assert merged["temperature"] == 0.9  # Overridden
        assert merged["max_tokens"] == 100  # Added


class TestGetProviderInfo:
    """Tests for get_provider_info function"""
    
    def test_get_provider_info(self):
        """Test getting provider information"""
        provider = MockProvider("test-provider", "test-model", key="value")
        info = get_provider_info(provider)
        
        assert info["provider_name"] == "test-provider"
        assert info["model"] == "test-model"
        assert info["provider_type"] == "MockProvider"
        assert "key" in info["config_keys"]


class TestCalculateTotalCost:
    """Tests for calculate_total_cost function"""
    
    def test_calculate_total_cost(self):
        """Test calculating total cost"""
        results = [
            CompletionResult("test1", 10, "model", "provider", 0.001),
            CompletionResult("test2", 20, "model", "provider", 0.002),
            CompletionResult("test3", 30, "model", "provider", 0.003)
        ]
        
        total = calculate_total_cost(results)
        
        assert total == 0.006
    
    def test_calculate_total_cost_empty(self):
        """Test calculating total cost with empty list"""
        total = calculate_total_cost([])
        
        assert total == 0.0


class TestCalculateTotalTokens:
    """Tests for calculate_total_tokens function"""
    
    def test_calculate_total_tokens(self):
        """Test calculating total tokens"""
        results = [
            CompletionResult("test1", 10, "model", "provider", 0.001),
            CompletionResult("test2", 20, "model", "provider", 0.002),
            CompletionResult("test3", 30, "model", "provider", 0.003)
        ]
        
        total = calculate_total_tokens(results)
        
        assert total == 60
    
    def test_calculate_total_tokens_empty(self):
        """Test calculating total tokens with empty list"""
        total = calculate_total_tokens([])
        
        assert total == 0
