"""
Tests for provider registry
"""

import pytest
from llm_provider import (
    ProviderRegistry,
    get_registry,
    register_provider,
    create_provider,
    list_providers,
    LLMProvider,
    CompletionResult
)


class MockProviderForRegistry(LLMProvider):
    """Mock provider for registry tests"""
    
    def complete(self, prompt: str, **kwargs) -> CompletionResult:
        return CompletionResult(
            content="test",
            tokens_used=10,
            model=self.model,
            provider=self.provider_name,
            cost=0.0
        )
    
    def stream(self, prompt: str, **kwargs):
        yield "test"
    
    def get_cost(self, tokens: int) -> float:
        return 0.0


class TestProviderRegistry:
    """Tests for ProviderRegistry"""
    
    def test_registry_initialization(self):
        """Test registry initialization"""
        registry = ProviderRegistry()
        
        assert registry._providers == {}
        assert registry._default_provider is None
    
    def test_register_provider(self):
        """Test registering a provider"""
        registry = ProviderRegistry()
        registry.register("test", MockProviderForRegistry)
        
        assert "test" in registry._providers
        assert registry._providers["test"] == MockProviderForRegistry
    
    def test_register_provider_as_default(self):
        """Test registering provider as default"""
        registry = ProviderRegistry()
        registry.register("test", MockProviderForRegistry, is_default=True)
        
        assert registry._default_provider == "test"
    
    def test_register_invalid_provider(self):
        """Test registering invalid provider class"""
        registry = ProviderRegistry()
        
        with pytest.raises(ValueError, match="must inherit from LLMProvider"):
            registry.register("test", str)
    
    def test_create_provider(self):
        """Test creating provider from registry"""
        registry = ProviderRegistry()
        registry.register("test", MockProviderForRegistry)
        
        provider = registry.create("test", model="test-model")
        
        assert isinstance(provider, MockProviderForRegistry)
        assert provider.model == "test-model"
        assert provider.provider_name == "test"
    
    def test_create_nonexistent_provider(self):
        """Test creating non-existent provider"""
        registry = ProviderRegistry()
        
        with pytest.raises(ValueError, match="not found"):
            registry.create("nonexistent", model="test")
    
    def test_list_providers(self):
        """Test listing registered providers"""
        registry = ProviderRegistry()
        registry.register("test1", MockProviderForRegistry)
        registry.register("test2", MockProviderForRegistry)
        
        providers = registry.list_providers()
        
        assert "test1" in providers
        assert "test2" in providers
    
    def test_get_default(self):
        """Test getting default provider"""
        registry = ProviderRegistry()
        registry.register("test", MockProviderForRegistry, is_default=True)
        
        assert registry.get_default() == "test"
    
    def test_set_default(self):
        """Test setting default provider"""
        registry = ProviderRegistry()
        registry.register("test", MockProviderForRegistry)
        registry.set_default("test")
        
        assert registry._default_provider == "test"
    
    def test_set_default_nonexistent(self):
        """Test setting non-existent provider as default"""
        registry = ProviderRegistry()
        
        with pytest.raises(ValueError, match="not registered"):
            registry.set_default("nonexistent")


class TestGlobalRegistry:
    """Tests for global registry functions"""
    
    def test_get_registry(self):
        """Test getting global registry"""
        registry = get_registry()
        
        assert isinstance(registry, ProviderRegistry)
    
    def test_register_provider_function(self):
        """Test register_provider function"""
        register_provider("test_func", MockProviderForRegistry)
        
        registry = get_registry()
        assert "test_func" in registry.list_providers()
    
    def test_create_provider_function(self):
        """Test create_provider function"""
        register_provider("test_create", MockProviderForRegistry)
        
        provider = create_provider("test_create", model="test-model")
        
        assert isinstance(provider, MockProviderForRegistry)
        assert provider.model == "test-model"
    
    def test_list_providers_function(self):
        """Test list_providers function"""
        providers = list_providers()
        
        assert isinstance(providers, list)
        # Should include built-in providers
        assert "openai" in providers
