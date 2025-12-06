"""
Test reporting functionality.
"""

from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
import json
from datetime import datetime

from test_agent.runner import TestResults
from test_agent.coverage import CoverageReport


@dataclass
class TestReport:
    """Complete test report."""
    timestamp: str
    test_results: TestResults
    coverage: Optional[CoverageReport] = None
    recommendations: list = None

    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []


class TestReporter:
    """Generate test reports."""

    def __init__(self, output_dir: str = "test-reports"):
        """
        Initialize reporter.

        Args:
            output_dir: Directory for reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(
        self,
        test_results: TestResults,
        coverage: Optional[CoverageReport] = None,
        format: str = "json"
    ) -> TestReport:
        """
        Generate a test report.

        Args:
            test_results: Test execution results
            coverage: Optional coverage report
            format: Report format ("json", "html", "text")

        Returns:
            TestReport object
        """
        # Generate recommendations
        recommendations = []
        if test_results.failed > 0:
            recommendations.append(f"{test_results.failed} tests failed - review failures")
        if coverage and coverage.percentage < 80:
            recommendations.append(f"Coverage is {coverage.percentage:.1f}% - aim for 80%+")
        if test_results.errors > 0:
            recommendations.append(f"{test_results.errors} errors occurred - check test setup")

        report = TestReport(
            timestamp=datetime.now().isoformat(),
            test_results=test_results,
            coverage=coverage,
            recommendations=recommendations
        )

        # Save report
        if format == "json":
            self._save_json_report(report)
        elif format == "html":
            self._save_html_report(report)
        else:
            self._save_text_report(report)

        return report

    def _save_json_report(self, report: TestReport):
        """Save report as JSON."""
        report_file = self.output_dir / f"report_{report.timestamp.replace(':', '-')}.json"
        with open(report_file, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=str)

    def _save_html_report(self, report: TestReport):
        """Save report as HTML."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .passed {{ color: green; }}
        .failed {{ color: red; }}
        .skipped {{ color: orange; }}
    </style>
</head>
<body>
    <h1>Test Report</h1>
    <p>Generated: {report.timestamp}</p>
    <h2>Results</h2>
    <ul>
        <li class="passed">Passed: {report.test_results.passed}</li>
        <li class="failed">Failed: {report.test_results.failed}</li>
        <li class="skipped">Skipped: {report.test_results.skipped}</li>
    </ul>
    {f'<h2>Coverage: {report.coverage.percentage:.1f}%</h2>' if report.coverage else ''}
    {f'<h2>Recommendations</h2><ul>{"".join(f"<li>{r}</li>" for r in report.recommendations)}</ul>' if report.recommendations else ''}
</body>
</html>"""
        report_file = self.output_dir / f"report_{report.timestamp.replace(':', '-')}.html"
        report_file.write_text(html)

    def _save_text_report(self, report: TestReport):
        """Save report as text."""
        text = f"""Test Report
Generated: {report.timestamp}

Results:
  Passed: {report.test_results.passed}
  Failed: {report.test_results.failed}
  Skipped: {report.test_results.skipped}
  Errors: {report.test_results.errors}
  Duration: {report.test_results.duration:.2f}s

"""
        if report.coverage:
            text += f"""Coverage: {report.coverage.percentage:.1f}%
  Lines: {report.coverage.lines_covered}/{report.coverage.lines_total}
  Branches: {report.coverage.branches_covered}/{report.coverage.branches_total}

"""
        if report.recommendations:
            text += "Recommendations:\n"
            for rec in report.recommendations:
                text += f"  - {rec}\n"

        report_file = self.output_dir / f"report_{report.timestamp.replace(':', '-')}.txt"
        report_file.write_text(text)

