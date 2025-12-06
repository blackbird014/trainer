"""Tests for test runner."""

import pytest
from test_agent.runner import TestRunner, TestResults


def test_runner_init():
    """Test runner initialization."""
    runner = TestRunner()
    assert runner.project_root is not None


def test_run_tests_nonexistent_module():
    """Test running tests for non-existent module."""
    runner = TestRunner()
    results = runner.run_tests(module="nonexistent-module")
    
    assert isinstance(results, TestResults)
    assert results.passed == 0
    assert results.failed == 0


def test_test_results_dataclass():
    """Test TestResults dataclass."""
    results = TestResults(
        passed=10,
        failed=2,
        skipped=1,
        errors=0,
        duration=5.5,
        failures=[]
    )
    
    assert results.passed == 10
    assert results.failed == 2
    assert results.duration == 5.5

