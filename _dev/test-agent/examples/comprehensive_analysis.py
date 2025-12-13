#!/usr/bin/env python3
"""
Comprehensive test analysis tool for all modules.

This tool uses test-agent to:
- Discover all modules and their tests
- Check for missing tests (coverage-based gap analysis)
- Run tests with coverage for each module
- Generate detailed coverage reports organized by module

Usage:
    python examples/comprehensive_analysis.py

Reports are saved to: reports/coverage-reports/
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Add test-agent to path (we're in the test-agent module)
script_dir = Path(__file__).parent
test_agent_src = script_dir.parent / "src"
sys.path.insert(0, str(test_agent_src))

from test_agent import TestAgent

def main():
    """Run comprehensive test analysis for all modules."""
    
    # Setup - detect project root (parent of _dev)
    script_dir = Path(__file__).parent
    test_agent_dir = script_dir.parent
    project_root = test_agent_dir.parent.parent  # Go up from _dev/test-agent to project root
    
    # Reports directory within test-agent module
    reports_dir = test_agent_dir / "reports" / "coverage-reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 80)
    print("Test Agent - Comprehensive Module Analysis")
    print("=" * 80)
    print(f"\nProject root: {project_root}")
    print(f"Reports directory: {reports_dir}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Initialize test agent
    agent = TestAgent(project_root=str(project_root))
    
    # Discover all modules
    modules = agent.discover_modules()
    print(f"Found {len(modules)} modules: {', '.join(modules)}\n")
    
    # Results storage
    all_results = {
        "timestamp": datetime.now().isoformat(),
        "modules": {}
    }
    
    # Process each module
    for module in modules:
        print("=" * 80)
        print(f"Module: {module}")
        print("=" * 80)
        
        module_results = {
            "module": module,
            "tests_discovered": [],
            "missing_tests": {},
            "coverage": None,
            "test_results": None,
            "reports_generated": []
        }
        
        # 1. Discover tests
        print("\n1. Discovering tests...")
        tests = agent.discover_tests(module)
        test_files = tests.get(module, [])
        module_results["tests_discovered"] = test_files
        print(f"   Found {len(test_files)} test files")
        if test_files:
            for test_file in test_files[:5]:  # Show first 5
                print(f"     - {test_file}")
            if len(test_files) > 5:
                print(f"     ... and {len(test_files) - 5} more")
        
        # 2. Check for missing tests
        print("\n2. Checking for missing tests...")
        try:
            missing = agent.find_missing_tests(module)
            module_results["missing_tests"] = missing
            
            if missing:
                total_missing = sum(len(items) for items in missing.values())
                print(f"   ⚠️  Found {total_missing} untested items:")
                for file_path, items in missing.items():
                    if items:
                        print(f"     {file_path}:")
                        for item in items[:3]:  # Show first 3
                            print(f"       - {item}")
                        if len(items) > 3:
                            print(f"       ... and {len(items) - 3} more")
            else:
                print("   ✓ No missing tests detected (or coverage data not available)")
        except Exception as e:
            print(f"   ⚠️  Could not check missing tests: {e}")
            module_results["missing_tests"] = {"error": str(e)}
        
        # 3. Run tests with coverage
        print("\n3. Running tests with coverage...")
        try:
            test_results = agent.run_tests(module=module, coverage=True, verbose=False)
            module_results["test_results"] = {
                "passed": test_results.passed,
                "failed": test_results.failed,
                "skipped": test_results.skipped,
                "errors": test_results.errors,
                "duration": test_results.duration
            }
            print(f"   Results: {test_results.passed} passed, {test_results.failed} failed, "
                  f"{test_results.skipped} skipped, {test_results.errors} errors")
            print(f"   Duration: {test_results.duration:.2f}s")
        except Exception as e:
            print(f"   ⚠️  Error running tests: {e}")
            module_results["test_results"] = {"error": str(e)}
        
        # 4. Get coverage report
        print("\n4. Analyzing coverage...")
        try:
            coverage = agent.check_coverage(module=module)
            module_results["coverage"] = {
                "percentage": coverage.percentage,
                "lines_covered": coverage.lines_covered,
                "lines_total": coverage.lines_total,
                "branches_covered": coverage.branches_covered if hasattr(coverage, 'branches_covered') else None,
                "branches_total": coverage.branches_total if hasattr(coverage, 'branches_total') else None,
                "module_breakdown": coverage.module_breakdown if hasattr(coverage, 'module_breakdown') else {}
            }
            print(f"   Coverage: {coverage.percentage:.1f}%")
            print(f"   Lines: {coverage.lines_covered}/{coverage.lines_total}")
        except Exception as e:
            print(f"   ⚠️  Error getting coverage: {e}")
            module_results["coverage"] = {"error": str(e)}
        
        # 5. Generate coverage report files
        print("\n5. Generating coverage reports...")
        module_report_dir = reports_dir / module
        module_report_dir.mkdir(exist_ok=True)
        
        # Save JSON report
        json_report = module_report_dir / "coverage_report.json"
        with open(json_report, "w") as f:
            json.dump(module_results, f, indent=2, default=str)
        module_results["reports_generated"].append(str(json_report.relative_to(reports_dir)))
        print(f"   ✓ JSON report: {json_report.relative_to(reports_dir)}")
        
        # Try to copy coverage HTML if it exists
        coverage_html = project_root / "_dev" / module / "htmlcov" / "index.html"
        if coverage_html.exists():
            import shutil
            html_report = module_report_dir / "coverage.html"
            shutil.copy(coverage_html, html_report)
            module_results["reports_generated"].append(str(html_report.relative_to(reports_dir)))
            print(f"   ✓ HTML report: {html_report.relative_to(reports_dir)}")
        
        # Save summary
        summary_file = module_report_dir / "summary.txt"
        with open(summary_file, "w") as f:
            f.write(f"Module: {module}\n")
            f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Tests Discovered: {len(test_files)}\n")
            if module_results["test_results"] and "error" not in module_results["test_results"]:
                f.write(f"Test Results: {module_results['test_results']['passed']} passed, "
                       f"{module_results['test_results']['failed']} failed\n")
            if module_results["coverage"] and "error" not in module_results["coverage"]:
                f.write(f"Coverage: {module_results['coverage']['percentage']:.1f}%\n")
                f.write(f"Lines: {module_results['coverage']['lines_covered']}/{module_results['coverage']['lines_total']}\n")
            if missing:
                total_missing = sum(len(items) for items in missing.values())
                f.write(f"\nMissing Tests: {total_missing} items\n")
        module_results["reports_generated"].append(str(summary_file.relative_to(reports_dir)))
        print(f"   ✓ Summary: {summary_file.relative_to(reports_dir)}")
        
        all_results["modules"][module] = module_results
        print()
    
    # Generate overall summary
    print("=" * 80)
    print("Overall Summary")
    print("=" * 80)
    
    summary_file = reports_dir / "overall_summary.json"
    with open(summary_file, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    
    # Print summary
    print(f"\nTotal modules analyzed: {len(modules)}")
    
    total_passed = sum(
        m.get("test_results", {}).get("passed", 0)
        for m in all_results["modules"].values()
        if m.get("test_results") and "error" not in m.get("test_results", {})
    )
    total_failed = sum(
        m.get("test_results", {}).get("failed", 0)
        for m in all_results["modules"].values()
        if m.get("test_results") and "error" not in m.get("test_results", {})
    )
    
    print(f"Total tests: {total_passed} passed, {total_failed} failed")
    
    # Coverage summary
    coverages = [
        m.get("coverage", {}).get("percentage", 0)
        for m in all_results["modules"].values()
        if m.get("coverage") and "error" not in m.get("coverage", {})
    ]
    if coverages:
        avg_coverage = sum(coverages) / len(coverages)
        print(f"Average coverage: {avg_coverage:.1f}%")
    
    # Missing tests summary
    modules_with_missing = [
        (name, m.get("missing_tests", {}))
        for name, m in all_results["modules"].items()
        if m.get("missing_tests") and "error" not in m.get("missing_tests", {}) and m.get("missing_tests")
    ]
    if modules_with_missing:
        print(f"\nModules with missing tests: {len(modules_with_missing)}")
        for name, missing in modules_with_missing:
            total = sum(len(items) for items in missing.values() if isinstance(items, list))
            if total > 0:
                print(f"  - {name}: {total} untested items")
    
    print(f"\n✓ All reports saved to: {reports_dir}")
    print(f"✓ Overall summary: {summary_file.relative_to(reports_dir)}")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()

