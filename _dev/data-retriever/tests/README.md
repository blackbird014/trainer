# Data Retriever Tests

This directory contains the test suite for the `data-retriever` module.

## Test Files

- **`test_base.py`** - Tests for base `DataRetriever` class and `RetrievalResult`
  - RetrievalResult creation and serialization
  - Cache integration
  - Rate limiting
  - Cache key generation

- **`test_cache.py`** - Tests for `DataCache` class
  - Basic cache operations (set/get)
  - Cache expiration (TTL)
  - Max size eviction (LRU)
  - Cache clearing and removal

- **`test_file_retriever.py`** - Tests for `FileRetriever`
  - Reading JSON files
  - Reading text files
  - Path resolution (absolute/relative)
  - Error handling (missing files, invalid paths)

- **`test_api_retriever.py`** - Tests for `APIRetriever`
  - GET requests
  - POST requests
  - Base URL handling
  - Error handling

- **`test_schema.py`** - Tests for schema validation
  - Field type validation
  - Required/optional fields
  - Schema validation
  - Schema serialization

## Running Tests

### Using pytest directly

```bash
# Install dependencies first
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_cache.py -v

# Run with coverage
pytest tests/ --cov=data_retriever --cov-report=html
```

### Using the test runner script

```bash
./run_tests.sh
```

### Using Python directly

```bash
python3 -m pytest tests/ -v
```

## Test Coverage

The test suite covers:
- ✅ Base abstraction layer
- ✅ Caching system
- ✅ File retriever
- ✅ API retriever
- ✅ Schema validation
- ⏭️ Yahoo Finance retriever (placeholder - needs implementation)
- ⏭️ SEC retriever (placeholder - needs implementation)
- ⏭️ Database retriever (placeholder - needs implementation)

## Adding New Tests

When adding new retrievers or features:

1. Create a new test file: `test_<feature>.py`
2. Follow the existing test patterns
3. Use pytest fixtures for common setup
4. Mock external dependencies (APIs, databases, etc.)
5. Test both success and error cases

## Example Test Structure

```python
"""Tests for FeatureX."""

import pytest
from data_retriever import FeatureX

def test_feature_x_basic():
    """Test basic functionality."""
    feature = FeatureX()
    result = feature.do_something()
    assert result.success

def test_feature_x_error():
    """Test error handling."""
    feature = FeatureX()
    result = feature.do_something_invalid()
    assert not result.success
    assert "error" in result.error.lower()
```

