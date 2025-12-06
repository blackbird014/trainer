"""
Test Agent - Automated testing framework for code and behavior validation.

Provides functionality for:
- Test discovery across modules
- Test execution (pytest integration)
- Test generation (optional, opt-in)
- Coverage analysis
- Mock generation
- Continuous testing with watch mode
"""

from test_agent.agent import TestAgent
from test_agent.discovery import ModuleDiscovery
from test_agent.runner import TestRunner
from test_agent.generator import TestGenerator, Test
from test_agent.coverage import CoverageAnalyzer
from test_agent.reporter import TestReporter

__all__ = [
    "TestAgent",
    "ModuleDiscovery",
    "TestRunner",
    "TestGenerator",
    "Test",
    "CoverageAnalyzer",
    "TestReporter",
]

__version__ = "0.1.0"

