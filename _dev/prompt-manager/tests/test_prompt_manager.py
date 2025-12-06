"""
Basic tests for PromptManager
"""

import pytest
from pathlib import Path
from prompt_manager import (
    PromptManager,
    PromptTemplate,
    PromptComposer,
    PromptCache,
    PromptValidator,
    ValidationResult
)


class TestPromptTemplate:
    """Tests for PromptTemplate"""
    
    def test_template_creation(self):
        """Test creating a template"""
        template = PromptTemplate("Hello {name}!")
        assert template.content == "Hello {name}!"
        assert "name" in template.get_variables()
    
    def test_template_fill(self):
        """Test filling template variables"""
        template = PromptTemplate("Hello {name}! You are {age} years old.")
        filled = template.fill({"name": "Alice", "age": "30"})
        assert filled == "Hello Alice! You are 30 years old."
    
    def test_template_missing_variable(self):
        """Test error when missing required variable"""
        template = PromptTemplate("Hello {name}!")
        with pytest.raises(ValueError, match="Missing required variables"):
            template.fill({})
    
    def test_template_from_file(self, tmp_path):
        """Test loading template from file"""
        template_file = tmp_path / "test_template.md"
        template_file.write_text("Hello {name}!")
        
        template = PromptTemplate.from_file(str(template_file))
        assert template.content == "Hello {name}!"
        assert str(template.path) == str(template_file)


class TestPromptComposer:
    """Tests for PromptComposer"""
    
    def test_sequential_composition(self):
        """Test sequential composition"""
        composer = PromptComposer()
        templates = [
            PromptTemplate("First prompt"),
            PromptTemplate("Second prompt")
        ]
        result = composer.compose(templates, strategy="sequential")
        assert "First prompt" in result
        assert "Second prompt" in result
        assert "---" in result
    
    def test_parallel_composition(self):
        """Test parallel composition"""
        composer = PromptComposer()
        templates = [
            PromptTemplate("First prompt"),
            PromptTemplate("Second prompt")
        ]
        result = composer.compose(templates, strategy="parallel")
        assert "Section 1" in result
        assert "Section 2" in result
    
    def test_hierarchical_composition(self):
        """Test hierarchical composition"""
        composer = PromptComposer()
        templates = [
            PromptTemplate("Main prompt"),
            PromptTemplate("Context prompt")
        ]
        result = composer.compose(templates, strategy="hierarchical")
        assert "Main prompt" in result
        assert "Additional Context" in result


class TestPromptCache:
    """Tests for PromptCache"""
    
    def test_cache_set_get(self):
        """Test basic cache set and get"""
        cache = PromptCache(max_size=10)
        cache.set("test_id", "test content")
        assert cache.get("test_id") == "test content"
    
    def test_cache_with_params(self):
        """Test cache with parameters"""
        cache = PromptCache(max_size=10)
        cache.set("test_id", "content1", params={"key": "value1"})
        cache.set("test_id", "content2", params={"key": "value2"})
        
        assert cache.get("test_id", params={"key": "value1"}) == "content1"
        assert cache.get("test_id", params={"key": "value2"}) == "content2"
    
    def test_cache_invalidation(self):
        """Test cache invalidation"""
        cache = PromptCache(max_size=10)
        cache.set("test_id", "content")
        cache.invalidate("test_id")
        assert cache.get("test_id") is None
    
    def test_cache_lru_eviction(self):
        """Test LRU eviction when cache is full"""
        cache = PromptCache(max_size=2)
        cache.set("id1", "content1")
        cache.set("id2", "content2")
        cache.set("id3", "content3")  # Should evict id1
        
        assert cache.get("id1") is None
        assert cache.get("id2") == "content2"
        assert cache.get("id3") == "content3"


class TestPromptValidator:
    """Tests for PromptValidator"""
    
    def test_validate_missing_variables(self):
        """Test validation detects missing variables"""
        validator = PromptValidator()
        template = PromptTemplate("Hello {name}!")
        result = validator.validate(template, params={})
        
        assert not result.is_valid
        assert len(result.errors) > 0
        assert "Missing required variables" in result.errors[0]
    
    def test_validate_success(self):
        """Test successful validation"""
        validator = PromptValidator()
        template = PromptTemplate("Hello {name}!")
        result = validator.validate(template, params={"name": "Alice"})
        
        assert result.is_valid
        assert len(result.errors) == 0


class TestPromptManager:
    """Tests for PromptManager"""
    
    def test_manager_initialization(self):
        """Test PromptManager initialization"""
        manager = PromptManager(context_dir="test_dir", enable_metrics=False)
        assert manager.loader.context_dir is not None
        assert manager.cache is not None
    
    def test_manager_load_prompt(self, tmp_path):
        """Test loading a prompt"""
        prompt_file = tmp_path / "prompt.md"
        prompt_file.write_text("Hello {name}!")
        
        manager = PromptManager(enable_metrics=False)
        template = manager.load_prompt(str(prompt_file))
        assert isinstance(template, PromptTemplate)
        assert template.content == "Hello {name}!"
    
    def test_manager_fill_template(self):
        """Test filling a template"""
        manager = PromptManager(enable_metrics=False)
        template = PromptTemplate("Hello {name}!")
        filled = manager.fill_template(template, {"name": "Alice"})
        assert filled == "Hello Alice!"

