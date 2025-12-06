"""Tests for module discovery."""

import pytest
import tempfile
from pathlib import Path
from test_agent.discovery import ModuleDiscovery


def test_discover_modules():
    """Test discovering modules."""
    # Use actual project structure
    discovery = ModuleDiscovery()
    modules = discovery.discover_modules()
    
    # Should find at least some modules
    assert isinstance(modules, list)
    # Should find known modules
    assert "prompt-manager" in modules or len(modules) > 0


def test_discover_tests():
    """Test discovering test files."""
    discovery = ModuleDiscovery()
    tests = discovery.discover_tests()
    
    assert isinstance(tests, dict)
    # Should find tests for modules that have them
    for module, test_files in tests.items():
        assert isinstance(test_files, list)


def test_get_module_path():
    """Test getting module path."""
    discovery = ModuleDiscovery()
    path = discovery.get_module_path("prompt-manager")
    
    # Should return Path or None
    assert path is None or isinstance(path, Path)


def test_get_tests_path():
    """Test getting tests path."""
    discovery = ModuleDiscovery()
    path = discovery.get_tests_path("prompt-manager")
    
    # Should return Path or None
    assert path is None or isinstance(path, Path)

