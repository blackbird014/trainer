"""
Test runner functionality using pytest.
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
import subprocess
import json
import sys
from dataclasses import dataclass


@dataclass
class TestResults:
    """Test execution results."""
    passed: int
    failed: int
    skipped: int
    errors: int
    duration: float
    failures: List[Dict[str, Any]]
    module: Optional[str] = None


class TestRunner:
    """Run tests using pytest."""

    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize test runner.

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

    def run_tests(
        self,
        module: Optional[str] = None,
        test_path: Optional[str] = None,
        verbose: bool = True,
        coverage: bool = False,
        **kwargs
    ) -> TestResults:
        """
        Run tests for a module or specific test path.

        Args:
            module: Module name (e.g., "prompt-manager")
            test_path: Specific test file or path
            verbose: Enable verbose output
            coverage: Enable coverage reporting
            **kwargs: Additional pytest arguments

        Returns:
            TestResults object
        """
        # Build pytest command
        cmd = [sys.executable, "-m", "pytest"]

        if verbose:
            cmd.append("-v")

        if coverage:
            # Specify source directory for coverage
            if module:
                cmd.extend(["--cov=src", "--cov-report=json", "--cov-report=term"])
            else:
                cmd.extend(["--cov", "--cov-report=json", "--cov-report=term"])

        # Determine test path and working directory
        working_dir = self.project_root
        if test_path:
            cmd.append(test_path)
        elif module:
            mod_path = self.dev_dir / module
            tests_dir = mod_path / "tests"
            if tests_dir.exists():
                # Run from module directory for proper coverage
                working_dir = mod_path.resolve()  # Use absolute path
                cmd.append("tests/")
            else:
                return TestResults(
                    passed=0,
                    failed=0,
                    skipped=0,
                    errors=0,
                    duration=0.0,
                    failures=[],
                    module=module
                )
        else:
            # Run all tests in _dev
            cmd.append(str(self.dev_dir))
            working_dir = self.dev_dir.resolve()

        # Add any additional kwargs as pytest args
        for key, value in kwargs.items():
            if value is True:
                cmd.append(f"--{key.replace('_', '-')}")
            elif value is not False and value is not None:
                cmd.append(f"--{key.replace('_', '-')}={value}")

        # Run pytest
        try:
            result = subprocess.run(
                cmd,
                cwd=str(working_dir),  # Convert Path to string for subprocess
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            # Parse output (basic parsing)
            output = result.stdout + result.stderr
            
            # Parse test results - try multiple methods
            import re
            
            # Method 1: Count " PASSED", " FAILED", etc. (pytest verbose format)
            passed = output.count(" PASSED")
            failed = output.count(" FAILED")
            skipped = output.count(" SKIPPED")
            errors = output.count(" ERROR")
            
            # Method 2: Parse from summary line (e.g., "34 passed in 2.56s")
            if passed == 0 and failed == 0 and skipped == 0:
                passed_match = re.search(r'(\d+)\s+passed', output, re.IGNORECASE)
                failed_match = re.search(r'(\d+)\s+failed', output, re.IGNORECASE)
                skipped_match = re.search(r'(\d+)\s+skipped', output, re.IGNORECASE)
                if passed_match:
                    passed = int(passed_match.group(1))
                if failed_match:
                    failed = int(failed_match.group(1))
                if skipped_match:
                    skipped = int(skipped_match.group(1))
            
            # Method 3: Parse from pytest's final summary
            # Look for lines like "=== 34 passed in 2.56s ==="
            summary_match = re.search(r'===?\s*(\d+)\s+passed', output, re.IGNORECASE)
            if summary_match and passed == 0:
                passed = int(summary_match.group(1))

            # Try to extract duration
            duration = 0.0
            for line in output.split("\n"):
                if "seconds" in line and "passed" in line.lower():
                    try:
                        # Extract number before "seconds"
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part == "seconds" and i > 0:
                                duration = float(parts[i-1])
                                break
                    except (ValueError, IndexError):
                        pass

            return TestResults(
                passed=passed,
                failed=failed,
                skipped=skipped,
                errors=errors,
                duration=duration,
                failures=[],  # Would need more sophisticated parsing
                module=module
            )

        except subprocess.TimeoutExpired:
            return TestResults(
                passed=0,
                failed=0,
                skipped=0,
                errors=1,
                duration=300.0,
                failures=[{"error": "Test execution timeout"}],
                module=module
            )
        except Exception as e:
            return TestResults(
                passed=0,
                failed=0,
                skipped=0,
                errors=1,
                duration=0.0,
                failures=[{"error": str(e)}],
                module=module
            )

    def run_integration_tests(
        self,
        modules: List[str],
        **kwargs
    ) -> TestResults:
        """
        Run integration tests across multiple modules.

        Args:
            modules: List of module names
            **kwargs: Additional pytest arguments

        Returns:
            TestResults object
        """
        # Look for integration test directories
        test_paths = []
        for module in modules:
            mod_path = self.dev_dir / module
            integration_dir = mod_path / "tests" / "integration"
            if integration_dir.exists():
                test_paths.append(str(integration_dir))

        if not test_paths:
            return TestResults(
                passed=0,
                failed=0,
                skipped=0,
                errors=0,
                duration=0.0,
                failures=[],
                module="integration"
            )

        # Run all integration tests
        return self.run_tests(test_path=" ".join(test_paths), **kwargs)

