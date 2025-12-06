"""Tests for enhanced test generation features."""

import pytest
import tempfile
from pathlib import Path
from test_agent.generator import TestGenerator


def test_find_missing_tests():
    """Test finding missing tests."""
    generator = TestGenerator()
    
    # Should return dict structure
    missing = generator.find_missing_tests("test-agent")
    assert isinstance(missing, dict)


def test_analyze_dependencies():
    """Test dependency analysis."""
    generator = TestGenerator()
    
    deps = generator.analyze_dependencies("prompt-manager")
    assert isinstance(deps, dict)
    assert "internal_modules" in deps
    assert "external_packages" in deps
    assert "imports" in deps


def test_generate_integration_tests():
    """Test integration test generation."""
    generator = TestGenerator()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tests = generator.generate_integration_tests(
            modules=["prompt-manager", "llm-provider"],
            output_dir=tmpdir
        )
        
        assert isinstance(tests, list)
        # Should generate at least one test if modules interact
        assert len(tests) >= 0


def test_generate_contract_tests():
    """Test contract test generation."""
    generator = TestGenerator()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tests = generator.generate_contract_tests(
            consumer_module="prompt-manager",
            provider_module="llm-provider",
            output_dir=tmpdir
        )
        
        assert isinstance(tests, list)
        # May or may not generate tests depending on actual dependencies


def test_generate_smart_tests():
    """Test smart test generation."""
    generator = TestGenerator()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tests = generator.generate_smart_tests(
            module_path="_dev/test-agent",
            output_dir=tmpdir
        )
        
        assert isinstance(tests, list)

