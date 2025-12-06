# Running Tests

## Prerequisites

1. Activate your virtual environment:
```bash
source /path/to/venv/bin/activate  # or your venv activation command
```

2. Install dependencies:
```bash
cd _dev/llm-provider
pip install -e ".[dev]"
```

## Running Tests

### Run all tests:
```bash
pytest tests/ -v
```

### Run specific test file:
```bash
pytest tests/test_base.py -v
pytest tests/test_providers.py -v
pytest tests/test_registry.py -v
```

### Run with coverage:
```bash
pytest tests/ --cov=llm_provider --cov-report=html
```

### Run specific test:
```bash
pytest tests/test_base.py::TestCompletionResult::test_completion_result_creation -v
```

## Test Structure

- `test_base.py` - Tests for base LLMProvider and CompletionResult
- `test_litellm_wrapper.py` - Tests for LiteLLM wrapper
- `test_providers.py` - Tests for all provider implementations
- `test_registry.py` - Tests for provider registry
- `test_utils.py` - Tests for utility functions

## Notes

- Most tests use mocks to avoid requiring actual API keys
- Some tests (like SageMaker) require boto3 to be installed
- Tests are designed to run without network access (mocked)

