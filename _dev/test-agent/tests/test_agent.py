"""Tests for main TestAgent class."""

import pytest
from test_agent import TestAgent


def test_agent_init():
    """Test agent initialization."""
    agent = TestAgent(enable_metrics=False)
    assert agent.discovery is not None
    assert agent.runner is not None
    assert agent.generator is not None
    assert agent.coverage is not None


def test_discover_modules():
    """Test discovering modules."""
    agent = TestAgent(enable_metrics=False)
    modules = agent.discover_modules()
    
    assert isinstance(modules, list)


def test_discover_tests():
    """Test discovering tests."""
    agent = TestAgent(enable_metrics=False)
    tests = agent.discover_tests()
    
    assert isinstance(tests, dict)

