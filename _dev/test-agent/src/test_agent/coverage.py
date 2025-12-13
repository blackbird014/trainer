"""
Coverage analysis functionality.
"""

from typing import Dict, Optional, List
from pathlib import Path
import json
import subprocess
import sys
from dataclasses import dataclass


@dataclass
class CoverageReport:
    """Coverage report data."""
    percentage: float
    lines_covered: int
    lines_total: int
    branches_covered: int
    branches_total: int
    module_breakdown: Dict[str, float]
    module: Optional[str] = None


class CoverageAnalyzer:
    """Analyze test coverage."""

    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize coverage analyzer.

        Args:
            project_root: Root directory of the project
        """
        if project_root is None:
            current = Path.cwd()
            while current != current.parent:
                if (current / "_dev").exists():
                    project_root = str(current)
                    break
                current = current.parent
            if project_root is None:
                project_root = str(Path.cwd())

        self.project_root = Path(project_root)
        self.dev_dir = self.project_root / "_dev"
        self.dev_dir = self.project_root / "_dev"

    def check_coverage(
        self,
        module: Optional[str] = None,
        threshold: Optional[float] = None
    ) -> CoverageReport:
        """
        Check test coverage for a module or all modules.

        Args:
            module: Module name, or None for all modules
            threshold: Minimum coverage percentage (for validation)

        Returns:
            CoverageReport object
        """
        # Run pytest with coverage
        from test_agent.runner import TestRunner
        runner = TestRunner(str(self.project_root))

        # Run tests with coverage
        result = runner.run_tests(module=module, coverage=True)

        # Try to read coverage JSON report
        # Coverage file is written in the module directory when running from there
        coverage_file = None
        if module:
            mod_path = self.dev_dir / module
            # Coverage file is named "coverage.json" (not ".coverage.json")
            coverage_file = mod_path / "coverage.json"
        
        if not coverage_file or not coverage_file.exists():
            # Try project root
            coverage_file = self.project_root / "coverage.json"
            if not coverage_file.exists():
                coverage_file = self.project_root / ".coverage.json"

        if coverage_file.exists():
            try:
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)

                totals = coverage_data.get("totals", {})
                percentage = totals.get("percent_covered", 0.0)
                lines_covered = totals.get("covered_lines", 0)
                lines_total = totals.get("num_statements", 0)
                branches_covered = totals.get("covered_branches", 0)
                branches_total = totals.get("num_branches", 0)

                # Module breakdown
                files = coverage_data.get("files", {})
                module_breakdown = {}
                for file_path, file_data in files.items():
                    mod_name = self._extract_module_name(file_path)
                    if mod_name:
                        file_percent = file_data.get("summary", {}).get("percent_covered", 0.0)
                        if mod_name not in module_breakdown:
                            module_breakdown[mod_name] = []
                        module_breakdown[mod_name].append(file_percent)

                # Average per module
                for mod_name in module_breakdown:
                    percentages = module_breakdown[mod_name]
                    module_breakdown[mod_name] = sum(percentages) / len(percentages)

                return CoverageReport(
                    percentage=percentage,
                    lines_covered=lines_covered,
                    lines_total=lines_total,
                    branches_covered=branches_covered,
                    branches_total=branches_total,
                    module_breakdown=module_breakdown,
                    module=module
                )
            except Exception:
                pass

        # Fallback: use coverage command
        try:
            cmd = [sys.executable, "-m", "coverage", "report", "--format=json"]
            if module:
                mod_path = self.dev_dir / module
                if mod_path.exists():
                    cmd.extend(["--include", f"{mod_path}/src/*"])

            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                coverage_data = json.loads(result.stdout)
                totals = coverage_data.get("totals", {})
                return CoverageReport(
                    percentage=totals.get("percent_covered", 0.0),
                    lines_covered=totals.get("covered_lines", 0),
                    lines_total=totals.get("num_statements", 0),
                    branches_covered=totals.get("covered_branches", 0),
                    branches_total=totals.get("num_branches", 0),
                    module_breakdown={},
                    module=module
                )
        except Exception:
            pass

        # Return empty report if coverage can't be determined
        return CoverageReport(
            percentage=0.0,
            lines_covered=0,
            lines_total=0,
            branches_covered=0,
            branches_total=0,
            module_breakdown={},
            module=module
        )

    def _extract_module_name(self, file_path: str) -> Optional[str]:
        """Extract module name from file path."""
        parts = Path(file_path).parts
        if "_dev" in parts:
            idx = parts.index("_dev")
            if idx + 1 < len(parts):
                return parts[idx + 1]
        return None

