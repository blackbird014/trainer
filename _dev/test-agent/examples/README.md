# Test Agent Examples

This directory contains example scripts demonstrating various features of the test-agent module.

## Basic Usage

- **`basic_usage.py`**: Demonstrates basic test discovery, execution, and coverage checking.

## API Usage

- **`api_usage_demo.py`**: Shows how to interact with the test-agent API service via HTTP requests.

## Enhanced Generation

- **`enhanced_generation.py`**: Demonstrates advanced test generation features:
  - Finding missing tests
  - Analyzing module dependencies
  - Generating integration tests
  - Generating contract tests
  - Smart generation from docstrings/type hints

## Comprehensive Analysis

- **`comprehensive_analysis.py`**: Complete test analysis tool for all modules:
  - Discovers all modules and their tests
  - Checks for missing tests (coverage-based gap analysis)
  - Runs tests with coverage for each module
  - Generates detailed coverage reports organized by module
  - Outputs reports to `reports/coverage-reports/`

**Usage:**
```bash
cd _dev/test-agent
python examples/comprehensive_analysis.py
```

**Output:**
- JSON reports per module with detailed analysis
- Text summaries for quick review
- HTML coverage reports (if available)
- Overall summary across all modules

## CI/CD Integration

- **`ci_cd_integration.md`**: Comprehensive guide for integrating test-agent into CI/CD pipelines, specifically GitHub Actions.

## Running Examples

### Basic Usage Example

```bash
cd _dev/test-agent
python3 examples/basic_usage.py
```

### Enhanced Generation Example

```bash
cd _dev/test-agent
python3 examples/enhanced_generation.py
```

### API Usage Demo

First, start the API service:

```bash
cd _dev/test-agent
python3 api_service.py
```

Then in another terminal:

```bash
cd _dev/test-agent
python3 examples/api_usage_demo.py
```

### Comprehensive Analysis

Run analysis for all modules:

```bash
cd _dev/test-agent
python3 examples/comprehensive_analysis.py
```

Reports are saved to `reports/coverage-reports/` directory.

### Dashboard

Start the web dashboard:

```bash
cd _dev/test-agent
python tools/dashboard.py
```

Access at: http://localhost:8889/

See `tools/README.md` for details.

## Generated Tests

All test generation features write tests to `tests/generated/` directories within each module. These are starting points - review and enhance them as needed!

- **Basic generation**: `tests/generated/test_auto_*.py`
- **Smart generation**: `tests/generated/test_smart_*.py`
- **Missing tests**: `tests/generated/test_auto_missing_*.py`
- **Integration tests**: `tests/integration/generated/test_auto_*_integration.py`
- **Contract tests**: `tests/integration/generated/test_auto_*_contract.py`

