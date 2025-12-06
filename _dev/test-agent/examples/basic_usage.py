#!/usr/bin/env python3
"""
Basic usage examples for test-agent module.
"""

from test_agent import TestAgent


def example_discover_modules():
    """Example: Discover modules."""
    print("=" * 60)
    print("Discover Modules Example")
    print("=" * 60)

    agent = TestAgent(enable_metrics=False)
    modules = agent.discover_modules()
    print(f"✓ Found {len(modules)} modules:")
    for module in modules:
        print(f"  - {module}")


def example_discover_tests():
    """Example: Discover tests."""
    print("\n" + "=" * 60)
    print("Discover Tests Example")
    print("=" * 60)

    agent = TestAgent(enable_metrics=False)
    tests = agent.discover_tests()
    print(f"✓ Found tests in {len(tests)} modules:")
    for module, test_files in tests.items():
        if test_files:
            print(f"  - {module}: {len(test_files)} test files")


def example_run_tests():
    """Example: Run tests."""
    print("\n" + "=" * 60)
    print("Run Tests Example")
    print("=" * 60)

    agent = TestAgent(enable_metrics=False)
    
    # Discover modules first
    modules = agent.discover_modules()
    if not modules:
        print("No modules found")
        return

    # Run tests for first module (if it has tests)
    module = modules[0]
    print(f"Running tests for {module}...")
    
    results = agent.run_tests(module=module, verbose=False)
    print(f"✓ Results:")
    print(f"  - Passed: {results.passed}")
    print(f"  - Failed: {results.failed}")
    print(f"  - Skipped: {results.skipped}")
    print(f"  - Duration: {results.duration:.2f}s")


def example_check_coverage():
    """Example: Check coverage."""
    print("\n" + "=" * 60)
    print("Check Coverage Example")
    print("=" * 60)

    agent = TestAgent(enable_metrics=False)
    
    modules = agent.discover_modules()
    if not modules:
        print("No modules found")
        return

    module = modules[0]
    print(f"Checking coverage for {module}...")
    
    coverage = agent.check_coverage(module=module)
    print(f"✓ Coverage: {coverage.percentage:.1f}%")
    print(f"  - Lines: {coverage.lines_covered}/{coverage.lines_total}")
    print(f"  - Branches: {coverage.branches_covered}/{coverage.branches_total}")


if __name__ == "__main__":
    try:
        example_discover_modules()
        example_discover_tests()
        example_run_tests()
        example_check_coverage()
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()

