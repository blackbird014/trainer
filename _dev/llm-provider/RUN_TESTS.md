# Running Tests and Examples

## Quick Start

### 1. Activate Your Virtual Environment

```bash
# Example (adjust path to your venv):
source /path/to/venv/bin/activate

# Or if using conda:
conda activate your-env-name
```

### 2. Install Dependencies

```bash
cd _dev/llm-provider
pip install -e ".[dev]"
```

This will install:
- The llm-provider package in editable mode
- Development dependencies (pytest, pytest-cov, black, ruff)
- Core dependency (litellm)

### 3. Run Tests

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_base.py -v

# Run with coverage
pytest tests/ --cov=llm_provider --cov-report=html

# Run specific test
pytest tests/test_base.py::TestCompletionResult::test_completion_result_creation -v
```

### 4. Run Examples

```bash
# Basic usage example
python examples/basic_usage.py

# All providers example
python examples/all_providers.py

# Registry usage
python examples/registry_usage.py

# Configuration examples
python examples/configuration_example.py

# Integration examples (require other modules)
python examples/integration_prompt_manager.py
python examples/integration_security.py
```

## Expected Test Results

The test suite includes:
- ✅ **test_base.py** - Base classes and CompletionResult (should all pass)
- ✅ **test_litellm_wrapper.py** - LiteLLM wrapper (uses mocks, should all pass)
- ✅ **test_providers.py** - All provider implementations (uses mocks, should all pass)
- ✅ **test_registry.py** - Provider registry (should all pass)
- ✅ **test_utils.py** - Utility functions (should all pass)

All tests use mocks and should pass without requiring actual API keys.

## Troubleshooting

### Import Errors
If you get import errors, make sure:
1. You're in the `_dev/llm-provider` directory
2. The package is installed: `pip install -e ".[dev]"`
3. Your Python path includes the src directory

### Missing Dependencies
If pytest or other dependencies are missing:
```bash
pip install -e ".[dev]"
```

### LiteLLM Import Errors
If litellm is not found:
```bash
pip install litellm>=1.0.0
```

## Example Output

When tests pass, you should see:
```
tests/test_base.py::TestCompletionResult::test_completion_result_creation PASSED
tests/test_base.py::TestCompletionResult::test_completion_result_validation PASSED
...
========================= X passed in Y.YYs =========================
```

