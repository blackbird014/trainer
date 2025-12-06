"""
Tests for configuration management
"""

import pytest
import tempfile
import os
import json
from llm_provider import ProviderConfig, LLMProviderConfig


class TestProviderConfig:
    """Tests for ProviderConfig"""
    
    def test_provider_config_creation(self):
        """Test creating ProviderConfig"""
        config = ProviderConfig(
            provider="openai",
            model="gpt-4",
            api_key="test-key",
            temperature=0.7
        )
        
        assert config.provider == "openai"
        assert config.model == "gpt-4"
        assert config.config == {"api_key": "test-key", "temperature": 0.7}
    
    def test_provider_config_to_dict(self):
        """Test converting ProviderConfig to dict"""
        config = ProviderConfig(
            provider="openai",
            model="gpt-4",
            api_key="test-key"
        )
        
        config_dict = config.to_dict()
        
        assert config_dict["provider"] == "openai"
        assert config_dict["model"] == "gpt-4"
        assert config_dict["api_key"] == "test-key"
    
    def test_provider_config_from_dict(self):
        """Test creating ProviderConfig from dict"""
        config_dict = {
            "provider": "openai",
            "model": "gpt-4",
            "api_key": "test-key"
        }
        
        config = ProviderConfig.from_dict(config_dict)
        
        assert config.provider == "openai"
        assert config.model == "gpt-4"
        assert config.config == {"api_key": "test-key"}
    
    def test_provider_config_from_env(self):
        """Test creating ProviderConfig from environment"""
        os.environ["LLM_PROVIDER"] = "openai"
        os.environ["LLM_MODEL"] = "gpt-4"
        os.environ["LLM_API_KEY"] = "test-key"
        
        config = ProviderConfig.from_env()
        
        assert config is not None
        assert config.provider == "openai"
        assert config.model == "gpt-4"
        assert config.config.get("api_key") == "test-key"
        
        # Cleanup
        del os.environ["LLM_PROVIDER"]
        del os.environ["LLM_MODEL"]
        del os.environ["LLM_API_KEY"]
    
    def test_provider_config_from_env_not_set(self):
        """Test ProviderConfig.from_env when not set"""
        # Ensure env vars are not set
        for key in ["LLM_PROVIDER", "LLM_MODEL"]:
            if key in os.environ:
                del os.environ[key]
        
        config = ProviderConfig.from_env()
        
        assert config is None
    
    def test_provider_config_from_json_file(self):
        """Test loading ProviderConfig from JSON file"""
        config_dict = {
            "provider": "openai",
            "model": "gpt-4",
            "api_key": "test-key"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_dict, f)
            temp_path = f.name
        
        try:
            config = ProviderConfig.from_file(temp_path)
            
            assert config.provider == "openai"
            assert config.model == "gpt-4"
            assert config.config == {"api_key": "test-key"}
        finally:
            os.unlink(temp_path)
    
    def test_provider_config_from_yaml_file(self):
        """Test loading ProviderConfig from YAML file"""
        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML not installed")
        
        config_dict = {
            "provider": "openai",
            "model": "gpt-4",
            "api_key": "test-key"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_dict, f)
            temp_path = f.name
        
        try:
            config = ProviderConfig.from_file(temp_path)
            
            assert config.provider == "openai"
            assert config.model == "gpt-4"
            assert config.config == {"api_key": "test-key"}
        finally:
            os.unlink(temp_path)
    
    def test_provider_config_from_file_not_found(self):
        """Test loading ProviderConfig from nonexistent file"""
        with pytest.raises(FileNotFoundError):
            ProviderConfig.from_file("/nonexistent/path/config.json")
    
    def test_provider_config_from_file_unsupported_format(self):
        """Test loading ProviderConfig from unsupported format"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Unsupported"):
                ProviderConfig.from_file(temp_path)
        finally:
            os.unlink(temp_path)


class TestLLMProviderConfig:
    """Tests for LLMProviderConfig"""
    
    def test_llm_provider_config_initialization(self):
        """Test LLMProviderConfig initialization"""
        config = LLMProviderConfig()
        
        assert config.providers == {}
        assert config.default_provider is None
    
    def test_add_provider(self):
        """Test adding provider to config"""
        config = LLMProviderConfig()
        provider_config = ProviderConfig(
            provider="openai",
            model="gpt-4"
        )
        
        config.add_provider("openai", provider_config)
        
        assert "openai" in config.providers
        assert config.providers["openai"] == provider_config
    
    def test_get_provider(self):
        """Test getting provider from config"""
        config = LLMProviderConfig()
        provider_config = ProviderConfig(
            provider="openai",
            model="gpt-4"
        )
        config.add_provider("openai", provider_config)
        
        retrieved = config.get_provider("openai")
        
        assert retrieved == provider_config
    
    def test_get_default_provider(self):
        """Test getting default provider"""
        config = LLMProviderConfig()
        provider_config = ProviderConfig(
            provider="openai",
            model="gpt-4"
        )
        config.add_provider("openai", provider_config)
        config.set_default("openai")
        
        retrieved = config.get_provider()
        
        assert retrieved == provider_config
    
    def test_set_default_provider(self):
        """Test setting default provider"""
        config = LLMProviderConfig()
        provider_config = ProviderConfig(
            provider="openai",
            model="gpt-4"
        )
        config.add_provider("openai", provider_config)
        
        config.set_default("openai")
        
        assert config.default_provider == "openai"
    
    def test_set_default_nonexistent_provider(self):
        """Test setting default to nonexistent provider"""
        config = LLMProviderConfig()
        
        with pytest.raises(ValueError, match="not found"):
            config.set_default("nonexistent")
    
    def test_llm_provider_config_from_json_file(self):
        """Test loading LLMProviderConfig from JSON file"""
        config_dict = {
            "providers": {
                "openai": {
                    "provider": "openai",
                    "model": "gpt-4",
                    "api_key": "test-key"
                }
            },
            "default_provider": "openai"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_dict, f)
            temp_path = f.name
        
        try:
            config = LLMProviderConfig.from_file(temp_path)
            
            assert "openai" in config.providers
            assert config.default_provider == "openai"
        finally:
            os.unlink(temp_path)
    
    def test_llm_provider_config_to_dict(self):
        """Test converting LLMProviderConfig to dict"""
        config = LLMProviderConfig()
        provider_config = ProviderConfig(
            provider="openai",
            model="gpt-4"
        )
        config.add_provider("openai", provider_config)
        config.set_default("openai")
        
        config_dict = config.to_dict()
        
        assert "providers" in config_dict
        assert "default_provider" in config_dict
        assert config_dict["default_provider"] == "openai"

