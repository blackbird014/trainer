#!/usr/bin/env python3
"""
Enhanced test generation examples.

Demonstrates:
- Missing test detection
- Integration test generation
- Smart generation from docstrings
- Contract test generation
"""

from test_agent import TestAgent


def example_find_missing_tests():
    """Example: Find missing tests."""
    print("=" * 80)
    print("Find Missing Tests Example")
    print("=" * 80)

    agent = TestAgent(enable_metrics=False)
    
    module = "format-converter"
    print(f"\nAnalyzing {module} for missing tests...")
    
    missing = agent.find_missing_tests(module)
    
    if missing:
        print(f"\n✓ Found missing tests in {len(missing)} files:")
        for file_path, items in missing.items():
            print(f"\n  {file_path}:")
            for item in items[:5]:  # Show first 5
                print(f"    - {item}")
            if len(items) > 5:
                print(f"    ... and {len(items) - 5} more")
    else:
        print(f"\n✓ No missing tests found (or all covered)")


def example_generate_missing_tests():
    """Example: Generate tests for missing coverage."""
    print("\n" + "=" * 80)
    print("Generate Missing Tests Example")
    print("=" * 80)

    agent = TestAgent(enable_metrics=False)
    
    module = "test-agent"
    print(f"\nGenerating tests for missing coverage in {module}...")
    
    tests = agent.generate_missing_tests(module)
    
    print(f"\n✓ Generated {len(tests)} tests")
    print(f"  Tests written to: _dev/{module}/tests/generated/")
    for test in tests[:3]:
        print(f"    - test_auto_{test.name}.py")


def example_analyze_dependencies():
    """Example: Analyze module dependencies."""
    print("\n" + "=" * 80)
    print("Analyze Dependencies Example")
    print("=" * 80)

    agent = TestAgent(enable_metrics=False)
    
    module = "prompt-manager"
    print(f"\nAnalyzing dependencies for {module}...")
    
    deps = agent.analyze_dependencies(module)
    
    print(f"\n✓ Dependencies found:")
    print(f"  Internal modules: {len(deps['internal_modules'])}")
    if deps['internal_modules']:
        for mod in deps['internal_modules']:
            print(f"    - {mod}")
    
    print(f"\n  External packages: {len(deps['external_packages'])}")
    if deps['external_packages']:
        for pkg in deps['external_packages'][:5]:
            print(f"    - {pkg}")
        if len(deps['external_packages']) > 5:
            print(f"    ... and {len(deps['external_packages']) - 5} more")


def example_generate_integration_tests():
    """Example: Generate integration tests."""
    print("\n" + "=" * 80)
    print("Generate Integration Tests Example")
    print("=" * 80)

    agent = TestAgent(enable_metrics=False)
    
    modules = ["prompt-manager", "llm-provider", "data-retriever"]
    print(f"\nGenerating integration tests for: {', '.join(modules)}")
    
    tests = agent.generate_integration_tests(modules)
    
    print(f"\n✓ Generated {len(tests)} integration tests")
    for test in tests:
        print(f"    - {test.name} ({test.test_type})")
        print(f"      Target: {test.target}")


def example_generate_contract_tests():
    """Example: Generate contract tests."""
    print("\n" + "=" * 80)
    print("Generate Contract Tests Example")
    print("=" * 80)

    agent = TestAgent(enable_metrics=False)
    
    consumer = "prompt-manager"
    provider = "llm-provider"
    print(f"\nGenerating contract tests:")
    print(f"  Consumer: {consumer}")
    print(f"  Provider: {provider}")
    
    tests = agent.generate_contract_tests(consumer, provider)
    
    print(f"\n✓ Generated {len(tests)} contract tests")
    for test in tests:
        print(f"    - {test.name}")
        print(f"      Tests contract: {test.target}")


def example_smart_generation():
    """Example: Smart test generation."""
    print("\n" + "=" * 80)
    print("Smart Test Generation Example")
    print("=" * 80)

    agent = TestAgent(enable_metrics=False)
    
    module_path = "_dev/format-converter"
    print(f"\nGenerating smart tests for {module_path}...")
    print("  (Uses docstrings and type hints)")
    
    tests = agent.generate_tests(
        module_path=module_path,
        strategy="smart"
    )
    
    print(f"\n✓ Generated {len(tests)} smart tests")
    print(f"  Tests written to: {module_path}/tests/generated/")


if __name__ == "__main__":
    try:
        example_find_missing_tests()
        example_analyze_dependencies()
        example_generate_integration_tests()
        example_generate_contract_tests()
        example_smart_generation()
        
        print("\n" + "=" * 80)
        print("All Enhanced Generation Examples Complete!")
        print("=" * 80)
        print("\nNote: Generated tests are written to tests/generated/ directories")
        print("Review and enhance them as needed - they're starting points!")
        
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()

