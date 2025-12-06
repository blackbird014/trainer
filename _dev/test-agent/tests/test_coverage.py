"""Tests for coverage analyzer."""

import pytest
from test_agent.coverage import CoverageAnalyzer, CoverageReport


def test_coverage_analyzer_init():
    """Test coverage analyzer initialization."""
    analyzer = CoverageAnalyzer()
    assert analyzer.project_root is not None


def test_check_coverage():
    """Test checking coverage."""
    analyzer = CoverageAnalyzer()
    report = analyzer.check_coverage()
    
    assert isinstance(report, CoverageReport)
    assert 0 <= report.percentage <= 100


def test_coverage_report_dataclass():
    """Test CoverageReport dataclass."""
    report = CoverageReport(
        percentage=85.5,
        lines_covered=1000,
        lines_total=1200,
        branches_covered=500,
        branches_total=600,
        module_breakdown={"module1": 90.0}
    )
    
    assert report.percentage == 85.5
    assert report.lines_covered == 1000

