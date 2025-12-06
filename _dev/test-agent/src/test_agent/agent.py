"""
Main TestAgent class that orchestrates all testing functionality.
"""

from typing import List, Optional, Dict, Any
from pathlib import Path

from test_agent.discovery import ModuleDiscovery
from test_agent.runner import TestRunner, TestResults
from test_agent.generator import TestGenerator, Test
from test_agent.coverage import CoverageAnalyzer, CoverageReport
from test_agent.reporter import TestReporter, TestReport


class TestAgent:
    """
    Main test agent class for automated testing.
    
    Non-invasive: Never modifies existing tests
    Opt-in: Test generation is explicit, not automatic
    Discovery-based: Finds modules/tests automatically
    """

    def __init__(
        self,
        project_root: Optional[str] = None,
        enable_metrics: bool = True
    ):
        """
        Initialize test agent.

        Args:
            project_root: Root directory of the project
            enable_metrics: Enable Prometheus metrics
        """
        self.enable_metrics = enable_metrics
        self.discovery = ModuleDiscovery(project_root)
        self.runner = TestRunner(project_root)
        self.generator = TestGenerator(project_root)
        self.coverage = CoverageAnalyzer(project_root)
        self.reporter = TestReporter()

        if enable_metrics:
            from test_agent.metrics import MetricsCollector
            self.metrics = MetricsCollector()
        else:
            self.metrics = None

    def discover_modules(self) -> List[str]:
        """
        Discover all modules in the project.

        Returns:
            List of module names
        """
        return self.discovery.discover_modules()

    def discover_tests(self, module: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Discover test files in modules.

        Args:
            module: Specific module name, or None for all modules

        Returns:
            Dictionary mapping module names to test file paths
        """
        return self.discovery.discover_tests(module)

    def run_tests(
        self,
        module: Optional[str] = None,
        test_path: Optional[str] = None,
        coverage: bool = False,
        **kwargs
    ) -> TestResults:
        """
        Run tests for a module or specific test path.

        Args:
            module: Module name
            test_path: Specific test file or path
            coverage: Enable coverage reporting
            **kwargs: Additional pytest arguments

        Returns:
            TestResults object
        """
        results = self.runner.run_tests(
            module=module,
            test_path=test_path,
            coverage=coverage,
            **kwargs
        )

        # Track metrics
        if self.metrics:
            self.metrics.track_test_run(
                module=module or "all",
                passed=results.passed,
                failed=results.failed,
                skipped=results.skipped,
                errors=results.errors,
                duration=results.duration
            )

        return results

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
        results = self.runner.run_integration_tests(modules, **kwargs)

        # Track metrics
        if self.metrics:
            self.metrics.track_integration_test_run(
                modules=",".join(modules),
                passed=results.passed,
                failed=results.failed,
                duration=results.duration
            )

        return results

    def generate_tests(
        self,
        module_path: str,
        strategy: str = "comprehensive",
        output_dir: Optional[str] = None
    ) -> List[Test]:
        """
        Generate tests for a module (opt-in, explicit).

        Args:
            module_path: Path to module
            strategy: Generation strategy ("comprehensive", "minimal", "smart", "missing")
            output_dir: Output directory for generated tests

        Returns:
            List of generated Test objects
        """
        if strategy == "smart":
            tests = self.generator.generate_smart_tests(
                module_path=module_path,
                output_dir=output_dir
            )
        elif strategy == "missing":
            # Extract module name from path
            module_name = Path(module_path).name
            tests = self.generator.generate_missing_tests(
                module=module_name,
                output_dir=output_dir
            )
        else:
            tests = self.generator.generate_tests(
                module_path=module_path,
                strategy=strategy,
                output_dir=output_dir
            )

        # Track metrics
        if self.metrics:
            self.metrics.track_test_generation(
                module=module_path,
                count=len(tests)
            )

        return tests

    def find_missing_tests(self, module: str) -> Dict[str, List[str]]:
        """
        Find functions/classes that lack test coverage.

        Args:
            module: Module name

        Returns:
            Dictionary mapping file paths to lists of untested items
        """
        return self.generator.find_missing_tests(module)

    def generate_missing_tests(
        self,
        module: str,
        output_dir: Optional[str] = None
    ) -> List[Test]:
        """
        Generate tests only for missing coverage.

        Args:
            module: Module name
            output_dir: Output directory

        Returns:
            List of generated Test objects
        """
        tests = self.generator.generate_missing_tests(module, output_dir)

        if self.metrics:
            self.metrics.track_test_generation(
                module=module,
                count=len(tests)
            )

        return tests

    def analyze_dependencies(self, module: str) -> Dict[str, List[str]]:
        """
        Analyze module dependencies.

        Args:
            module: Module name

        Returns:
            Dictionary with dependency information
        """
        return self.generator.analyze_dependencies(module)

    def generate_integration_tests(
        self,
        modules: List[str],
        output_dir: Optional[str] = None
    ) -> List[Test]:
        """
        Generate integration tests for module interactions.

        Args:
            modules: List of module names to test together
            output_dir: Output directory

        Returns:
            List of generated Test objects
        """
        tests = self.generator.generate_integration_tests(modules, output_dir)

        if self.metrics:
            self.metrics.track_test_generation(
                module="+".join(modules),
                count=len(tests)
            )

        return tests

    def generate_contract_tests(
        self,
        consumer_module: str,
        provider_module: str,
        output_dir: Optional[str] = None
    ) -> List[Test]:
        """
        Generate contract tests between modules.

        Args:
            consumer_module: Module that uses the provider
            provider_module: Module that provides the interface
            output_dir: Output directory

        Returns:
            List of generated Test objects
        """
        tests = self.generator.generate_contract_tests(
            consumer_module,
            provider_module,
            output_dir
        )

        if self.metrics:
            self.metrics.track_test_generation(
                module=f"{consumer_module}->{provider_module}",
                count=len(tests)
            )

        return tests

    def check_coverage(
        self,
        module: Optional[str] = None,
        threshold: Optional[float] = None
    ) -> CoverageReport:
        """
        Check test coverage for a module or all modules.

        Args:
            module: Module name, or None for all modules
            threshold: Minimum coverage percentage

        Returns:
            CoverageReport object
        """
        report = self.coverage.check_coverage(module=module, threshold=threshold)

        # Track metrics
        if self.metrics:
            self.metrics.track_coverage(
                module=module or "all",
                percentage=report.percentage
            )

        return report

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
            format: Report format

        Returns:
            TestReport object
        """
        return self.reporter.generate_report(test_results, coverage, format)

    def watch_and_test(self, module: str) -> None:
        """
        Watch for file changes and run tests automatically.

        Args:
            module: Module name to watch
        """
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
        except ImportError:
            raise ImportError(
                "watchdog not installed. Install with: pip install watchdog"
            )

        class TestHandler(FileSystemEventHandler):
            def __init__(self, agent, module):
                self.agent = agent
                self.module = module

            def on_modified(self, event):
                if event.src_path.endswith('.py'):
                    print(f"\nFile changed: {event.src_path}")
                    print("Running tests...")
                    results = self.agent.run_tests(module=self.module)
                    print(f"Results: {results.passed} passed, {results.failed} failed")

        mod_path = self.discovery.get_module_path(module)
        if mod_path is None:
            raise ValueError(f"Module not found: {module}")

        event_handler = TestHandler(self, module)
        observer = Observer()
        observer.schedule(event_handler, str(mod_path), recursive=True)
        observer.start()

        print(f"Watching {module} for changes... Press Ctrl+C to stop.")
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

