# Logging System Guide

## Overview

The PromptManager includes a comprehensive logging system with:
- **Structured JSON logging** (easy to parse and query)
- **File logging** (for persistence)
- **Prometheus metrics** (for Grafana dashboards)
- **Database logging** (extensible)
- **Automatic operation tracking**

## Quick Start

### Basic Usage

```python
from prompt_manager import PromptManager, LogLevel

# Enable logging with file output
manager = PromptManager(
    context_dir="information/context",
    log_file="logs/prompt_manager.log",
    log_level=LogLevel.INFO,
    enable_metrics=True
)

# Operations are automatically logged
contexts = manager.load_contexts(["biotech/01-introduction.md"])
```

### Custom Logger

```python
from prompt_manager import setup_logger, LogLevel

# Create custom logger
logger = setup_logger(
    name="my_app",
    log_file="logs/app.log",
    log_level=LogLevel.DEBUG,
    enable_json=True,
    enable_metrics=True
)

# Use with PromptManager
manager = PromptManager(logger=logger)
```

## Log Formats

### JSON Format (Default)

Logs are written as JSON for easy parsing:

```json
{
  "timestamp": "2024-12-03T12:00:00.000000",
  "level": "INFO",
  "logger": "prompt_manager",
  "message": "Loaded 3 context files",
  "operation": "load_contexts",
  "duration": 0.123,
  "tokens": 4827,
  "context_files": ["biotech/01-introduction.md"],
  "context_size_chars": 16897
}
```

### Human-Readable Format

For console output, you can disable JSON:

```python
logger = setup_logger(
    enable_json=False  # Human-readable format
)
```

## Log Levels

```python
from prompt_manager import LogLevel

# Available levels
LogLevel.DEBUG      # Detailed debugging
LogLevel.INFO       # General information (default)
LogLevel.WARNING    # Warnings
LogLevel.ERROR      # Errors
LogLevel.CRITICAL   # Critical errors
```

## Prometheus Metrics

### Enable Metrics

```python
manager = PromptManager(
    enable_metrics=True  # Enable Prometheus metrics
)
```

### Available Metrics

- `prompt_manager_operations_total` - Total operations (by operation, status)
- `prompt_manager_operation_duration_seconds` - Operation duration (histogram)
- `prompt_manager_tokens_total` - Total tokens (by operation, type)
- `prompt_manager_cost_total` - Total cost in USD (by operation, model)
- `prompt_manager_cache_hits_total` - Cache hits (by cache_type)
- `prompt_manager_cache_misses_total` - Cache misses (by cache_type)

### Expose Metrics Endpoint

```python
from flask import Flask
from prompt_manager import PromptManager

app = Flask(__name__)
manager = PromptManager(enable_metrics=True)

@app.route('/metrics')
def metrics():
    handler = manager.logger.get_metrics_endpoint()
    if handler:
        return handler()
    return "Metrics not available", 404
```

### Grafana Dashboard

1. **Set up Prometheus** to scrape `/metrics` endpoint
2. **Create Grafana dashboard** with queries like:
   - `rate(prompt_manager_operations_total[5m])` - Operations per second
   - `histogram_quantile(0.95, prompt_manager_operation_duration_seconds)` - P95 latency
   - `sum(prompt_manager_cost_total)` - Total cost
   - `rate(prompt_manager_cache_hits_total[5m]) / rate(prompt_manager_cache_misses_total[5m])` - Cache hit ratio

## Database Logging

### Setup Database Handler

```python
from prompt_manager import setup_logger, DatabaseLogHandler

logger = setup_logger(
    enable_database=True,
    db_connection="postgresql://user:pass@localhost/logs"
)

# Logs will be written to database
```

### Custom Database Handler

```python
from prompt_manager import DatabaseLogHandler

class CustomDBHandler(DatabaseLogHandler):
    def emit(self, record):
        # Custom database insertion logic
        log_data = self.extract_log_data(record)
        self.db.insert("logs", log_data)
```

## Automatic Logging

PromptManager automatically logs:

- **load_contexts()** - Context loading with file count, size, duration, tokens
- **fill_template()** - Template filling with variables, duration, tokens
- **compose()** - Prompt composition with strategy, template count, duration, tokens
- **get_cached()** - Cache hits/misses
- **Errors** - All exceptions with stack traces

## Custom Logging

### Add Custom Log Messages

```python
manager.logger.info(
    "Custom operation completed",
    operation="my_custom_op",
    duration=0.5,
    tokens=1000,
    cost=0.03,
    custom_field="value"
)
```

### Log Levels

```python
manager.logger.debug("Debug message")
manager.logger.info("Info message")
manager.logger.warning("Warning message")
manager.logger.error("Error message")
manager.logger.critical("Critical message")
```

## Log File Management

### Rotating Logs

Use Python's `RotatingFileHandler`:

```python
import logging
from logging.handlers import RotatingFileHandler
from prompt_manager import PromptManagerLogger

logger = PromptManagerLogger(
    name="prompt_manager",
    enable_json=True
)

# Add rotating handler
handler = RotatingFileHandler(
    "logs/prompt_manager.log",
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
handler.setFormatter(JSONFormatter())
logger.logger.addHandler(handler)
```

### Log Parsing

Parse JSON logs easily:

```python
import json

with open("logs/prompt_manager.log") as f:
    for line in f:
        log_entry = json.loads(line)
        if log_entry["level"] == "ERROR":
            print(f"Error: {log_entry['message']}")
```

## Integration Examples

### Flask Application

```python
from flask import Flask
from prompt_manager import PromptManager, LogLevel

app = Flask(__name__)

manager = PromptManager(
    log_file="logs/app.log",
    log_level=LogLevel.INFO,
    enable_metrics=True
)

@app.route('/analyze')
def analyze():
    # Operations automatically logged
    contexts = manager.load_contexts(["context.md"])
    return "Analysis complete"

@app.route('/metrics')
def metrics():
    return manager.logger.get_metrics_endpoint()()
```

### FastAPI Application

```python
from fastapi import FastAPI
from prompt_manager import PromptManager

app = FastAPI()
manager = PromptManager(enable_metrics=True)

@app.get("/metrics")
async def metrics():
    handler = manager.logger.get_metrics_endpoint()
    if handler:
        return handler()
    return {"error": "Metrics not available"}
```

## Best Practices

1. **Use JSON format** for production (easy to parse and query)
2. **Set appropriate log levels** (INFO for production, DEBUG for development)
3. **Enable metrics** for monitoring and alerting
4. **Rotate log files** to prevent disk space issues
5. **Parse logs** for analysis (ELK stack, Splunk, etc.)
6. **Monitor costs** via Prometheus/Grafana
7. **Alert on errors** using log aggregation tools

## Dependencies

### Required
- Python `logging` module (built-in)

### Optional
- `prometheus-client` - For Prometheus metrics
  ```bash
  pip install prometheus-client
  # Or
  pip install -e ".[metrics]"
  ```

## See Also

- `example_logging.py` - Full working example
- `TOKEN_TRACKING_GUIDE.md` - Token tracking integration
- `README.md` - General documentation

