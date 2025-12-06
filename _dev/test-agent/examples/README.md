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

## Generated Tests

All test generation features write tests to `tests/generated/` directories within each module. These are starting points - review and enhance them as needed!

- **Basic generation**: `tests/generated/test_auto_*.py`
- **Smart generation**: `tests/generated/test_smart_*.py`
- **Missing tests**: `tests/generated/test_auto_missing_*.py`
- **Integration tests**: `tests/integration/generated/test_auto_*_integration.py`
- **Contract tests**: `tests/integration/generated/test_auto_*_contract.py`

