#!/usr/bin/env python3
"""
Demo: How to see test results via API service.

This shows how to interact with the test-agent API service.
"""

import requests
import json
import time

API_BASE = "http://localhost:8006"

def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

def demo_api_usage():
    """Demonstrate API usage."""
    
    print_section("Test Agent API - How to See Test Results")
    
    print("\n1. START THE API SERVICE:")
    print("-" * 80)
    print("In a terminal, run:")
    print("  cd _dev/test-agent")
    print("  python api_service.py")
    print("\nThe service will start on http://localhost:8006")
    print("Swagger UI will be available at: http://localhost:8006/docs")
    
    print("\n2. VIEW TEST RESULTS - Method 1: Swagger UI (Easiest)")
    print("-" * 80)
    print("Open in browser: http://localhost:8006/docs")
    print("\nSteps:")
    print("  a) Click on 'POST /run_tests'")
    print("  b) Click 'Try it out'")
    print("  c) Enter module name (e.g., 'format-converter')")
    print("  d) Set coverage: true (optional)")
    print("  e) Click 'Execute'")
    print("  f) See results in 'Response body' section")
    print("\nExample response:")
    print(json.dumps({
        "success": True,
        "results": {
            "passed": 33,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "duration": 0.15,
            "module": "format-converter"
        }
    }, indent=2))
    
    print("\n3. VIEW TEST RESULTS - Method 2: curl (Command Line)")
    print("-" * 80)
    print("Run tests for a module:")
    print("""
curl -X POST http://localhost:8006/run_tests \\
  -H "Content-Type: application/json" \\
  -d '{"module": "format-converter", "coverage": true}' | jq
""")
    print("\nRun all tests:")
    print("""
curl -X POST http://localhost:8006/run_tests \\
  -H "Content-Type: application/json" \\
  -d '{"coverage": true}' | jq
""")
    
    print("\n4. VIEW TEST RESULTS - Method 3: Python requests")
    print("-" * 80)
    print("""
import requests

# Run tests
response = requests.post(
    "http://localhost:8006/run_tests",
    json={"module": "format-converter", "coverage": True}
)

results = response.json()
print(f"Passed: {results['results']['passed']}")
print(f"Failed: {results['results']['failed']}")
print(f"Duration: {results['results']['duration']}s")
""")
    
    print("\n5. OTHER USEFUL ENDPOINTS")
    print("-" * 80)
    print("\nDiscover modules:")
    print("  GET http://localhost:8006/discover_modules")
    print("\nDiscover tests:")
    print("  GET http://localhost:8006/discover_tests?module=format-converter")
    print("\nCheck coverage:")
    print("  GET http://localhost:8006/check_coverage?module=format-converter")
    print("\nView metrics:")
    print("  GET http://localhost:8006/metrics")
    
    print("\n6. EXAMPLE: Complete Workflow")
    print("-" * 80)
    print("""
# 1. Discover modules
curl http://localhost:8006/discover_modules

# 2. Discover tests for a module
curl "http://localhost:8006/discover_tests?module=format-converter"

# 3. Run tests
curl -X POST http://localhost:8006/run_tests \\
  -H "Content-Type: application/json" \\
  -d '{"module": "format-converter", "coverage": true}'

# 4. Check coverage
curl "http://localhost:8006/check_coverage?module=format-converter"
""")
    
    print("\n7. VIEW RESULTS IN BROWSER")
    print("-" * 80)
    print("Best way: Use Swagger UI")
    print("  → http://localhost:8006/docs")
    print("\nThis provides:")
    print("  ✓ Interactive API explorer")
    print("  ✓ Try endpoints directly")
    print("  ✓ See request/response formats")
    print("  ✓ View test results in formatted JSON")
    
    print("\n" + "=" * 80)
    print("Summary: Easiest way is Swagger UI at http://localhost:8006/docs")
    print("=" * 80)

if __name__ == "__main__":
    demo_api_usage()

