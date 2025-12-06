# Test Agent

Automated testing framework for code and behavior validation across all modules.

## Features

- **Test Discovery**: Automatically discover modules and test files
- **Test Execution**: Run tests using pytest (non-invasive, respects existing tests)
- **Test Generation**: Optional test generation (opt-in, explicit, non-destructive)
  - Basic unit test generation
  - Smart generation from docstrings/type hints
  - Missing test detection (coverage-based)
  - Integration test generation (interface-based)
  - Contract test generation
- **Coverage Analysis**: Track test coverage per module
- **Integration Testing**: Run integration tests across modules
- **Dependency Analysis**: Analyze module dependencies and interactions
- **Watch Mode**: Continuous testing on file changes
- **Prometheus Metrics**: Built-in metrics for monitoring

## Design Principles

✅ **Non-Invasive**: Never modifies existing tests  
✅ **Opt-In**: Test generation is explicit, not automatic  
✅ **Discovery-Based**: Finds modules/tests automatically  
✅ **Configurable**: Works with your existing structure  
✅ **Generic**: Usable outside this project  

## Installation

```bash
pip install -e .
```

With optional dependencies:

```bash
# With watch mode support
pip install -e ".[watch]"

# All dependencies
pip install -e ".[all]"
```

## Quick Start

### Discover Modules

```python
from test_agent import TestAgent

agent = TestAgent()
modules = agent.discover_modules()
print(f"Found modules: {modules}")
```

### Run Tests

```python
# Run tests for a specific module
results = agent.run_tests(module="prompt-manager")

# Run all tests
results = agent.run_tests()

# Run with coverage
results = agent.run_tests(module="llm-provider", coverage=True)
```

### Check Coverage

```python
coverage = agent.check_coverage(module="prompt-manager")
print(f"Coverage: {coverage.percentage}%")
```

### Generate Tests (Optional, Opt-In)

```python
# Basic generation
tests = agent.generate_tests(
    module_path="_dev/prompt-manager",
    strategy="comprehensive"
)

# Smart generation (from docstrings/type hints)
tests = agent.generate_tests(
    module_path="_dev/prompt-manager",
    strategy="smart"
)

# Generate only missing tests
missing = agent.find_missing_tests("prompt-manager")
tests = agent.generate_missing_tests("prompt-manager")

# Generate integration tests
tests = agent.generate_integration_tests([
    "prompt-manager",
    "llm-provider"
])

# Generate contract tests
tests = agent.generate_contract_tests(
    consumer_module="prompt-manager",
    provider_module="llm-provider"
)
```

### Watch Mode

```python
# Watch for changes and auto-run tests
agent.watch_and_test("prompt-manager")
```

## API Service

The module includes a FastAPI service for exposing test functionality via REST API:

```bash
cd _dev/test-agent
python api_service.py
```

The service runs on port 8006 (configurable via `PORT` environment variable) and provides:

- `GET /discover_modules` - Discover all modules
- `GET /discover_tests` - Discover test files
- `POST /run_tests` - Run tests
- `POST /run_integration_tests` - Run integration tests
- `GET /check_coverage` - Check coverage
- `POST /generate_tests` - Generate tests (opt-in)
- `GET /find_missing_tests` - Find missing tests
- `POST /generate_missing_tests` - Generate missing tests
- `POST /generate_integration_tests` - Generate integration tests
- `POST /generate_contract_tests` - Generate contract tests
- `GET /analyze_dependencies` - Analyze module dependencies
- `GET /metrics` - Prometheus metrics endpoint
- `GET /health` - Health check

### Example API Usage

```bash
# Discover modules
curl http://localhost:8006/discover_modules

# Run tests
curl -X POST http://localhost:8006/run_tests \
  -H "Content-Type: application/json" \
  -d '{"module": "prompt-manager", "coverage": true}'

# Check coverage
curl http://localhost:8006/check_coverage?module=prompt-manager
```

## Prometheus Metrics

The module exposes Prometheus metrics at `/metrics` endpoint:

- `test_agent_test_runs_total` - Total test runs (by module, status)
- `test_agent_test_duration_seconds` - Test execution duration histogram
- `test_agent_tests_passed_total` - Total tests passed (by module)
- `test_agent_tests_failed_total` - Total tests failed (by module)
- `test_agent_coverage_percentage` - Coverage percentage gauge
- `test_agent_tests_generated_total` - Total tests generated (by module)
- `test_agent_integration_test_runs_total` - Integration test runs

### Monitoring Setup

1. **Start the API service**:
   ```bash
   cd _dev/test-agent
   python api_service.py
   ```

2. **Configure Prometheus** (already configured in centralized monitoring):
   The centralized monitoring at `_dev/monitoring/` is already configured to scrape test-agent on port 8006.

3. **View Grafana Dashboard**:
   - Start centralized monitoring: `cd _dev/monitoring && docker-compose up -d`
   - Access Grafana: http://localhost:3000
   - Navigate to "Test Agent Dashboard"

## API Reference

### TestAgent

Main agent class.

```python
agent = TestAgent(
    project_root="/path/to/project",  # Optional, auto-detects
    enable_metrics=True
)

# Discover modules
modules = agent.discover_modules()

# Discover tests
tests = agent.discover_tests(module="prompt-manager")

# Run tests
results = agent.run_tests(module="prompt-manager", coverage=True)

# Check coverage
coverage = agent.check_coverage(module="prompt-manager")

# Generate tests (opt-in)
tests = agent.generate_tests("_dev/prompt-manager")

# Watch mode
agent.watch_and_test("prompt-manager")
```

### TestResults

Test execution results.

```python
results = agent.run_tests(module="prompt-manager")
print(results.passed)   # Number of passed tests
print(results.failed)   # Number of failed tests
print(results.duration) # Execution duration in seconds
```

### CoverageReport

Coverage analysis results.

```python
coverage = agent.check_coverage(module="prompt-manager")
print(coverage.percentage)      # Coverage percentage
print(coverage.lines_covered)   # Lines covered
print(coverage.lines_total)     # Total lines
```

## How It Works

### Test Discovery

The agent automatically discovers:
- Modules in `_dev/` directory
- Test files in each module's `tests/` directory
- Integration tests in `tests/integration/` directories

### Test Execution

- Uses pytest under the hood
- Respects existing test structure
- Never modifies existing tests
- Supports all pytest features (fixtures, markers, etc.)

### Test Generation

- **Opt-in only**: Must explicitly call `generate_tests()`
- **Non-destructive**: Generated tests go to `tests/generated/` directory
- **Template-based**: Uses Jinja2 templates for generation
- **Respects existing tests**: Never overwrites existing test files

## Development

### Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in development mode
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

Or use the test runner:

```bash
./run_tests.sh
```

## Package Structure

```
test-agent/
├── src/
│   ├── test_agent/
│   │   ├── __init__.py
│   │   ├── agent.py              # Main TestAgent class
│   │   ├── discovery.py          # Module/test discovery
│   │   ├── runner.py              # Test execution (pytest)
│   │   ├── generator.py           # Test generation (opt-in)
│   │   ├── coverage.py             # Coverage analysis
│   │   ├── reporter.py             # Test reporting
│   │   ├── metrics.py              # Prometheus metrics
│   │   ├── templates/              # Test templates
│   │   └── mocks/                  # Pre-built mocks
│   └── tests/
├── examples/
│   └── basic_usage.py
├── api_service.py                 # FastAPI service
├── pyproject.toml
└── README.md
```

## Dependencies

### Core Dependencies
- `pytest>=7.0.0` - Test framework
- `pytest-cov>=4.0.0` - Coverage plugin
- `pytest-mock>=3.10.0` - Mocking utilities
- `coverage>=7.0.0` - Coverage analysis
- `jinja2>=3.1.0` - Template engine
- `prometheus-client>=0.19.0` - Metrics collection
- `fastapi>=0.104.0` - API framework
- `uvicorn[standard]>=0.24.0` - ASGI server

### Optional Dependencies
- `watchdog>=3.0.0` - File watching for watch mode

## Examples

See `examples/` directory for:
- Basic usage examples
- Module discovery
- Test execution
- Coverage checking

## License

MIT

