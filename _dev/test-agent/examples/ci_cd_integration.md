# CI/CD Integration Guide

## Overview

There are **two main approaches** for CI/CD integration:

1. **Use test-agent API** (via HTTP) - More flexible, centralized
2. **Use pytest directly** (standard) - Simpler, more common
3. **Hybrid approach** - Use test-agent for discovery/reporting, pytest for execution

## Approach 1: Direct pytest (Recommended for CI/CD)

**Why**: Simpler, faster, standard practice, better GitHub integration

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        module: [prompt-manager, llm-provider, data-retriever, format-converter, model-trainer, test-agent]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd _dev/${{ matrix.module }}
          pip install -e ".[dev]"
      
      - name: Run tests
        run: |
          cd _dev/${{ matrix.module }}
          pytest tests/ -v --cov=src --cov-report=xml --cov-report=html
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./_dev/${{ matrix.module }}/coverage.xml
          flags: ${{ matrix.module }}
      
      - name: Publish test results
        uses: EnricoMi/publish-unit-test-result-action@v2
        if: always()
        with:
          files: |
            _dev/${{ matrix.module }}/test-results.xml
```

**GitHub Visibility**:
- ✅ Test results appear in Actions tab
- ✅ Coverage reports in PR comments (via codecov)
- ✅ Test summary in PR checks
- ✅ Artifacts (HTML coverage reports)

## Approach 2: Use test-agent API

**Why**: Centralized, can use test-agent features (discovery, reporting)

```yaml
# .github/workflows/test-with-agent.yml
name: Tests via Test Agent

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install all modules
        run: |
          for module in _dev/*/; do
            if [ -f "$module/pyproject.toml" ]; then
              pip install -e "$module"
            fi
          done
      
      - name: Start test-agent API
        run: |
          cd _dev/test-agent
          python api_service.py &
          sleep 5
        env:
          PORT: 8006
      
      - name: Run tests via API
        run: |
          # Discover modules
          MODULES=$(curl -s http://localhost:8006/discover_modules | jq -r '.modules[]')
          
          # Run tests for each module
          for module in $MODULES; do
            echo "Testing $module..."
            curl -X POST http://localhost:8006/run_tests \
              -H "Content-Type: application/json" \
              -d "{\"module\": \"$module\", \"coverage\": true}" \
              > test-results-$module.json
          done
      
      - name: Generate summary
        run: |
          python << EOF
          import json
          import glob
          
          results = []
          for f in glob.glob('test-results-*.json'):
              with open(f) as file:
                  results.append(json.load(file))
          
          total_passed = sum(r['results']['passed'] for r in results)
          total_failed = sum(r['results']['failed'] for r in results)
          
          print(f"## Test Results Summary")
          print(f"- ✅ Passed: {total_passed}")
          print(f"- ❌ Failed: {total_failed}")
          EOF >> $GITHUB_STEP_SUMMARY
      
      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results
          path: test-results-*.json
```

## Approach 3: Hybrid (Best of Both Worlds)

**Use test-agent for discovery/reporting, pytest for execution**

```yaml
# .github/workflows/test-hybrid.yml
name: Tests (Hybrid)

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install test-agent
        run: |
          cd _dev/test-agent
          pip install -e .
      
      - name: Discover modules and tests
        id: discover
        run: |
          python << EOF
          from test_agent import TestAgent
          import json
          
          agent = TestAgent()
          modules = agent.discover_modules()
          tests = agent.discover_tests()
          
          with open('modules.json', 'w') as f:
              json.dump({'modules': modules, 'tests': tests}, f)
          
          print(f"Found {len(modules)} modules")
          EOF
      
      - name: Run tests (pytest)
        run: |
          python << EOF
          import json
          import subprocess
          import sys
          
          with open('modules.json') as f:
              data = json.load(f)
          
          failed = []
          for module in data['modules']:
              print(f"Testing {module}...")
              result = subprocess.run(
                  ['pytest', f'_dev/{module}/tests/', '-v', '--tb=short'],
                  capture_output=True,
                  text=True
              )
              
              if result.returncode != 0:
                  failed.append(module)
                  print(f"❌ {module} failed")
              else:
                  print(f"✅ {module} passed")
          
          if failed:
              print(f"\\nFailed modules: {', '.join(failed)}")
              sys.exit(1)
          EOF
      
      - name: Generate coverage report
        run: |
          python << EOF
          from test_agent import TestAgent
          import json
          
          agent = TestAgent()
          modules = agent.discover_modules()
          
          coverage_summary = {}
          for module in modules:
              coverage = agent.check_coverage(module=module)
              coverage_summary[module] = coverage.percentage
          
          # Write summary
          with open('coverage-summary.json', 'w') as f:
              json.dump(coverage_summary, f, indent=2)
          
          # Print to GitHub summary
          print("## Coverage Summary")
          for module, percent in coverage_summary.items():
              status = "✅" if percent >= 80 else "⚠️"
              print(f"{status} {module}: {percent:.1f}%")
          EOF >> $GITHUB_STEP_SUMMARY
```

## GitHub Visibility Options

### Option 1: GitHub Actions UI (Built-in)

**What you get**:
- Test results in Actions tab
- Pass/fail status per job
- Logs for debugging
- Artifacts download

**Setup**: Just run pytest in workflow (Approach 1)

### Option 2: PR Comments (via Actions)

```yaml
- name: Comment PR with test results
  uses: actions/github-script@v6
  if: github.event_name == 'pull_request'
  with:
    script: |
      const fs = require('fs');
      const results = JSON.parse(fs.readFileSync('test-results.json'));
      
      const body = `## Test Results
      - ✅ Passed: ${results.passed}
      - ❌ Failed: ${results.failed}
      - ⏱️ Duration: ${results.duration}s
      `;
      
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: body
      });
```

### Option 3: Test Reports (JUnit XML)

```yaml
- name: Run tests with JUnit output
  run: |
    pytest tests/ --junitxml=test-results.xml

- name: Publish test results
  uses: EnricoMi/publish-unit-test-result-action@v2
  if: always()
  with:
    files: test-results.xml
```

**What you get**:
- Test results in PR checks
- Expandable test list
- See which tests passed/failed
- Links to failed test logs

### Option 4: Coverage Reports (Codecov)

```yaml
- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
    flags: unittests
```

**What you get**:
- Coverage percentage in PR
- Coverage diff (what changed)
- Coverage trends over time
- File-by-file coverage

### Option 5: Custom Dashboard (test-agent API)

```yaml
- name: Start test-agent API
  run: |
    cd _dev/test-agent
    python api_service.py &
  
- name: Generate HTML report
  run: |
    curl -X POST http://localhost:8006/run_tests \
      -H "Content-Type: application/json" \
      -d '{"coverage": true}' | \
    python -c "
    import json, sys
    data = json.load(sys.stdin)
    # Generate HTML report
    " > test-report.html

- name: Upload report
  uses: actions/upload-artifact@v3
  with:
    name: test-report
    path: test-report.html
```

## Recommended Approach for Your Project

### For Monorepo (Current Structure)

**Use Approach 1 (Direct pytest)** with matrix strategy:

```yaml
# .github/workflows/test.yml
name: Test All Modules

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        module:
          - prompt-manager
          - prompt-security
          - llm-provider
          - data-retriever
          - format-converter
          - model-trainer
          - test-agent
    
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install and test
        run: |
          cd _dev/${{ matrix.module }}
          pip install -e ".[dev]"
          pytest tests/ -v --cov=src --cov-report=xml --junitxml=results.xml
      
      - name: Upload results
        uses: EnricoMi/publish-unit-test-result-action@v2
        if: always()
        with:
          files: _dev/${{ matrix.module }}/results.xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./_dev/${{ matrix.module }}/coverage.xml
          flags: ${{ matrix.module }}
```

**What you'll see on GitHub**:
- ✅ 7 separate test jobs (one per module)
- ✅ Each shows pass/fail independently
- ✅ Test results in PR checks
- ✅ Coverage reports per module
- ✅ Can see which module failed

### Alternative: Use test-agent for Integration Tests

```yaml
jobs:
  unit-tests:
    # ... pytest for each module (as above)
  
  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install all modules
        run: |
          for module in _dev/*/; do
            pip install -e "$module"
          done
      
      - name: Run integration tests via test-agent
        run: |
          cd _dev/test-agent
          pip install -e .
          python -c "
          from test_agent import TestAgent
          agent = TestAgent()
          results = agent.run_integration_tests([
              'prompt-manager',
              'llm-provider',
              'data-retriever',
              'format-converter'
          ])
          print(f'Integration tests: {results.passed} passed, {results.failed} failed')
          "
```

## Summary

**Best Practice for GitHub Visibility**:

1. **Unit Tests**: Use pytest directly (Approach 1)
   - Better GitHub integration
   - Standard practice
   - Faster execution

2. **Integration Tests**: Use test-agent
   - Tests module interactions
   - Uses test-agent's discovery
   - Can use test-agent's reporting

3. **Coverage**: Use codecov
   - Automatic PR comments
   - Coverage trends
   - File-by-file breakdown

4. **Test Reports**: Use JUnit XML + publish action
   - Test list in PR
   - See individual test results
   - Links to logs

**Result**: You'll have full visibility on GitHub:
- ✅ Test status per module
- ✅ Coverage reports
- ✅ Test results in PR
- ✅ Integration test results
- ✅ Artifacts (HTML reports)

