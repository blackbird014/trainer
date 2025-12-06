# Test Generation Enhancements

This document describes the enhanced test generation features added to test-agent.

## Overview

The test-agent module now supports advanced test generation capabilities beyond basic unit test templates:

1. **Missing Test Detection** - Coverage-based gap analysis
2. **Integration Test Generation** - Interface-based generation
3. **Smart Generation** - Docstring and type hint analysis
4. **Contract Test Generation** - Module interface validation
5. **Dependency Analysis** - Module dependency mapping

## Features

### 1. Missing Test Detection

Find functions and classes that lack test coverage.

**Python API:**
```python
from test_agent import TestAgent

agent = TestAgent()
missing = agent.find_missing_tests("prompt-manager")
# Returns: Dict[str, List[str]] mapping file paths to untested items
```

**REST API:**
```bash
GET /find_missing_tests?module=prompt-manager
```

**Generate Missing Tests:**
```python
tests = agent.generate_missing_tests("prompt-manager")
# Generates tests only for untested functions/classes
```

### 2. Dependency Analysis

Analyze module dependencies to understand module interactions.

**Python API:**
```python
deps = agent.analyze_dependencies("prompt-manager")
# Returns:
# {
#   "internal_modules": ["llm_provider", "prompt_security"],
#   "external_packages": ["fastapi", "pydantic", ...],
#   "imports": [...]
# }
```

**REST API:**
```bash
GET /analyze_dependencies?module=prompt-manager
```

### 3. Integration Test Generation

Generate integration tests based on module interactions.

**Python API:**
```python
tests = agent.generate_integration_tests([
    "prompt-manager",
    "llm-provider",
    "data-retriever"
])
# Generates tests in: tests/integration/generated/
```

**REST API:**
```bash
POST /generate_integration_tests
{
  "modules": ["prompt-manager", "llm-provider"],
  "output_dir": null
}
```

### 4. Contract Test Generation

Generate contract tests to verify module interfaces.

**Python API:**
```python
tests = agent.generate_contract_tests(
    consumer_module="prompt-manager",
    provider_module="llm-provider"
)
# Generates contract tests verifying interface compliance
```

**REST API:**
```bash
POST /generate_contract_tests
{
  "consumer_module": "prompt-manager",
  "provider_module": "llm-provider",
  "output_dir": null
}
```

### 5. Smart Generation

Generate tests using docstrings and type hints for better test quality.

**Python API:**
```python
tests = agent.generate_tests(
    module_path="_dev/prompt-manager",
    strategy="smart"  # Uses docstrings and type hints
)
```

**Features:**
- Extracts function signatures from type hints
- Uses docstrings to understand expected behavior
- Generates more context-aware test templates

## Test Generation Strategies

The `generate_tests` method now supports multiple strategies:

- **`comprehensive`** (default): Generate all tests
- **`minimal`**: Generate minimal test templates
- **`smart`**: Use docstrings and type hints
- **`missing`**: Generate only missing tests

## Generated Test Locations

- **Basic/Unit tests**: `tests/generated/test_auto_*.py`
- **Smart tests**: `tests/generated/test_smart_*.py`
- **Missing tests**: `tests/generated/test_auto_missing_*.py`
- **Integration tests**: `tests/integration/generated/test_auto_*_integration.py`
- **Contract tests**: `tests/integration/generated/test_auto_*_contract.py`

## Usage Examples

See `examples/enhanced_generation.py` for complete examples of all features.

## Implementation Details

### Missing Test Detection

- Scans source files for classes and functions
- Checks if corresponding tests exist
- Returns mapping of untested items

### Dependency Analysis

- Parses AST to find imports
- Distinguishes internal modules from external packages
- Maps module interactions

### Integration Test Generation

- Analyzes dependencies between modules
- Generates tests for module interactions
- Creates test templates for integration scenarios

### Contract Test Generation

- Verifies consumer-provider relationships
- Generates tests for interface compliance
- Tests error handling in contracts

### Smart Generation

- Extracts docstrings for context
- Parses type hints for signatures
- Generates more informed test templates

## API Endpoints

All features are available via both Python API and REST API:

**New REST Endpoints:**
- `GET /find_missing_tests` - Find missing tests
- `POST /generate_missing_tests` - Generate missing tests
- `POST /generate_integration_tests` - Generate integration tests
- `POST /generate_contract_tests` - Generate contract tests
- `GET /analyze_dependencies` - Analyze dependencies

**Enhanced Endpoint:**
- `POST /generate_tests` - Now supports `strategy` parameter ("smart", "missing", etc.)

## Notes

- All test generation is **opt-in** and **non-destructive**
- Generated tests are starting points - review and enhance as needed
- Tests are written to `tests/generated/` directories
- Integration and contract tests go to `tests/integration/generated/`

