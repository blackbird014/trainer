# Prompt Manager

A Python module for managing prompts with template support, context loading, composition, caching, and validation.

## Features

- **Template Engine**: Variable substitution with `{variable}` syntax
- **Context Loading**: Load and merge multiple context files
- **Prompt Composition**: Combine multiple prompts using different strategies
- **Caching**: LRU cache with TTL support to avoid redundant processing
- **Validation**: Check for missing variables, broken references, and template errors

## Installation

### Virtual Environment Setup (Recommended)

It's recommended to use a virtual environment to isolate dependencies:

```bash
# Create a virtual environment
python3 -m venv .venv

# Activate it (macOS/Linux)
source .venv/bin/activate

# Activate it (Windows)
# .venv\Scripts\activate

# Install the module in development mode
pip install -e .

# Install with dev dependencies (for testing)
pip install -e ".[dev]"
```

**In Cursor/VS Code:**
- Select the Python interpreter: `.venv/bin/python` (or `.venv\Scripts\python.exe` on Windows)
- Press `F1` → "Python: Select Interpreter" → Choose `.venv/bin/python`
- Cursor will automatically use the venv once selected

**Managing the Virtual Environment:**
```bash
# Activate (when you want to use it)
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate    # Windows

# Deactivate (when done)
deactivate

# Delete and recreate (if needed)
rm -rf .venv
python3 -m venv .venv

# Check if venv is active (look for (.venv) in prompt)
which python  # Should show .venv/bin/python when active
```

### Direct Installation (Without venv)

If you prefer not to use a virtual environment:

```bash
pip install -e .
```

## Quick Start

```python
from prompt_manager import PromptManager

# Initialize with context directory
manager = PromptManager(context_dir="information/context")

# Load a prompt template
template = manager.load_prompt("information/instructions/prompt.md")

# Fill template variables
filled = manager.fill_template(template, {
    "COMPANY_NAME": "Example Corp",
    "TICKER": "EXMP"
})

# Load contexts
contexts = manager.load_contexts([
    "biotech/01-introduction.md",
    "molecular-biology-foundations.md"
])

# Compose prompts
from prompt_manager import PromptComposer
composer = PromptComposer()
composed = composer.compose([template], strategy="sequential")
```

## API Reference

### PromptManager

Main class that orchestrates all functionality.

```python
manager = PromptManager(
    context_dir="information/context",  # Base directory for contexts
    cache_enabled=True,                  # Enable caching
    cache_max_size=100,                  # Max cache entries
    cache_ttl=3600                       # Cache TTL in seconds
)
```

#### Methods

- `load_prompt(prompt_path: str) -> PromptTemplate`: Load a prompt template
- `load_contexts(context_paths: List[str]) -> str`: Load and merge contexts
- `fill_template(template: PromptTemplate, params: Dict[str, Any]) -> str`: Fill template variables
- `compose(templates: List[PromptTemplate], strategy: str) -> str`: Compose multiple templates
- `get_cached(prompt_id: str, params: Optional[Dict]) -> Optional[str]`: Get cached prompt
- `cache_prompt(prompt_id: str, content: str, params: Optional[Dict], ttl: Optional[int])`: Cache a prompt
- `validate(template: PromptTemplate, params: Optional[Dict], context_paths: Optional[List[str]]) -> ValidationResult`: Validate a prompt

### PromptTemplate

Represents a prompt template with variable substitution.

```python
template = PromptTemplate("Hello {name}!")
filled = template.fill({"name": "World"})  # "Hello World!"
```

### PromptComposer

Composes multiple prompts using different strategies.

- `sequential`: Join prompts with separators (default)
- `parallel`: Format as parallel sections
- `hierarchical`: First prompt as main, others as contexts

### PromptCache

LRU cache with TTL support.

```python
cache = PromptCache(max_size=100, default_ttl=3600)
cache.set("prompt_id", "content", params={"key": "value"}, ttl=1800)
content = cache.get("prompt_id", params={"key": "value"})
```

### PromptValidator

Validates prompts and their dependencies.

```python
validator = PromptValidator(context_dir="information/context")
result = validator.validate(template, params={"name": "World"})
if result.is_valid:
    print("Valid!")
else:
    print(result.errors)
```

## Template Syntax

Templates use `{variable_name}` syntax for variable substitution:

```markdown
# Analysis for {COMPANY_NAME} ({TICKER})

## Context
{CONTEXT_CONTENT}

## Data
{DATA_JSON}
```

Variables must be valid Python identifiers (letters, numbers, underscore, starting with letter/underscore).

## Composition Strategies

### Sequential
Join prompts sequentially with separators:
```
Prompt 1
---
Prompt 2
```

### Parallel
Format as parallel sections:
```
## Section 1
Prompt 1

## Section 2
Prompt 2
```

### Hierarchical
First prompt as main, others as contexts:
```
Main Prompt
---
## Additional Context
### Context 1
Prompt 2
```

## Monitoring

The Prompt Manager module exposes Prometheus metrics at `/metrics` endpoint. For monitoring setup, see the centralized monitoring infrastructure:

**📊 [Centralized Monitoring Documentation](../../monitoring/README.md)**

The centralized monitoring setup includes:
- Prometheus for metrics collection
- Grafana dashboards for visualization
- Dashboards for all Trainer modules (prompt-manager, prompt-security, llm-provider)
- Overview dashboard aggregating all modules

**Quick Start:**
```bash
# Start centralized monitoring
cd ../monitoring
docker-compose up -d

# Access Grafana
open http://localhost:3000  # admin/admin
```

**Metrics Exposed:**
- `prompt_manager_operations_total` - Total operations by type and status
- `prompt_manager_operation_duration_seconds` - Operation duration histogram
- `prompt_manager_tokens_total` - Total tokens used
- `prompt_manager_cost_total` - Total cost in USD
- `prompt_manager_cache_hits_total` - Cache hits
- `prompt_manager_cache_misses_total` - Cache misses
- `prompt_manager_security_validation_total` - Security validations
- `prompt_manager_security_injection_detected_total` - Injections detected
- `prompt_manager_security_rate_limit_hits_total` - Rate limit hits

## Development

```bash
# Activate virtual environment first (if using one)
source .venv/bin/activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=prompt_manager

# Format code
black src/

# Lint code
ruff check src/
```

## License

MIT

