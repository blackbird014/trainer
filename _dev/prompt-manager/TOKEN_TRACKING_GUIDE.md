# Token Tracking Guide

## Overview

The PromptManager now includes **automatic token tracking** to help you monitor costs and usage. This feature estimates token counts and calculates costs based on model pricing.

## Quick Start

### Enable Token Tracking

```python
from prompt_manager import PromptManager

# Enable tracking with default model (GPT-4 pricing)
manager = PromptManager(
    context_dir="information/context",
    track_tokens=True,  # Enable tracking
    model="gpt-4"       # Set model for cost estimation
)
```

### View Usage Report

```python
# Get formatted report
report = manager.get_token_report()
print(report)

# Output:
# ================================================================================
# Token Usage Report
# ================================================================================
# Model: gpt-4
# Total Operations: 3
# 
# Total Usage:
#   Input Tokens:  6,549
#   Output Tokens: 0
#   Total Tokens:   6,549
# 
# Total Cost:
#   Input Cost:  $0.1965
#   Output Cost: $0.0000
#   Total Cost:  $0.1965
# ...
```

### Get Usage Statistics Programmatically

```python
# Get total usage
total = manager.get_token_usage()
print(f"Total tokens: {total['total_tokens']:,}")
print(f"Total cost: ${total['total_cost']:.4f}")

# Get per-operation stats
stats = manager.get_operation_stats()
for operation, op_stats in stats.items():
    print(f"{operation}: {op_stats['count']} operations, "
          f"${op_stats['total_cost']:.4f} total")
```

## Supported Models

The tracker includes pricing for common models:

- `gpt-4` - $0.03/1K input, $0.06/1K output
- `gpt-4-turbo` - $0.01/1K input, $0.03/1K output
- `gpt-3.5-turbo` - $0.0005/1K input, $0.0015/1K output
- `claude-3-opus` - $0.015/1K input, $0.075/1K output
- `claude-3-sonnet` - $0.003/1K input, $0.015/1K output
- `claude-3-haiku` - $0.00025/1K input, $0.00125/1K output
- `default` - Uses GPT-4 pricing

## Automatic Tracking

Token tracking happens automatically for these operations:

1. **`load_contexts()`** - Tracks context file loading
2. **`fill_template()`** - Tracks template variable filling
3. **`compose()`** - Tracks prompt composition

## Example Usage

```python
from prompt_manager import PromptManager
import json

# Initialize with tracking
manager = PromptManager(
    context_dir="information/context",
    track_tokens=True,
    model="gpt-4"
)

# Load contexts (tracked automatically)
contexts = manager.load_contexts([
    "biotech/01-introduction.md",
    "biotech/molecular-biology-foundations.md"
])

# Load and fill template (tracked automatically)
template = manager.load_prompt("instructions/prompt.md")
filled = manager.fill_template(template, {"COMPANY": "NVDA"})

# Compose prompt (tracked automatically)
from prompt_manager import PromptTemplate
final = manager.compose([
    PromptTemplate(contexts),
    PromptTemplate(filled)
])

# View costs
print(manager.get_token_report())

# Expected output shows:
# - load_contexts: ~4,800 tokens, $0.14
# - fill_template: ~400 tokens, $0.01
# - compose: ~1,300 tokens, $0.04
# Total: ~$0.19
```

## Advanced Usage

### Custom Model Pricing

You can add custom pricing by modifying `TokenTracker.PRICING`:

```python
from prompt_manager import TokenTracker

# Add custom model pricing
TokenTracker.PRICING["my-model"] = {
    "input": 0.002,   # $0.002 per 1K tokens
    "output": 0.004   # $0.004 per 1K tokens
}

# Use it
manager = PromptManager(track_tokens=True, model="my-model")
```

### Manual Token Tracking

You can also track tokens manually:

```python
from prompt_manager import TokenTracker

tracker = TokenTracker(model="gpt-4")

# Track by text (auto-estimates tokens)
tracker.track_text("my_operation", "Some text here")

# Track by exact token count
tracker.track_usage("my_operation", input_tokens=1000, output_tokens=500)

# Get report
print(tracker.get_report())
```

### Reset Tracking

Start fresh:

```python
manager.reset_token_tracking()
```

### Export History

Get raw usage data:

```python
tracker = manager.token_tracker
history = tracker.export_history()

# Returns list of TokenUsage objects as dictionaries
for entry in history:
    print(f"{entry['operation']}: {entry['total_tokens']} tokens")
```

## Token Estimation

The tracker uses a simple heuristic: **~4 characters per token** for English text. This is reasonably accurate but not perfect.

For more accurate estimation, you can use `tiktoken`:

```python
import tiktoken

def estimate_tokens_accurate(text, model="gpt-4"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))
```

## Cost Monitoring Best Practices

1. **Enable tracking in development** to understand costs
2. **Monitor per-operation costs** to identify expensive operations
3. **Use caching** to reduce repeated token usage
4. **Compare models** by switching model parameter
5. **Set budgets** based on tracked usage

## Integration with Production

For production monitoring:

```python
import logging

manager = PromptManager(track_tokens=True, model="gpt-4")

# After operations
usage = manager.get_token_usage()

# Log to your monitoring system
logging.info(f"Token usage: {usage['total_tokens']} tokens, "
             f"${usage['total_cost']:.4f} cost")

# Or send to metrics service
metrics.gauge("llm.tokens", usage['total_tokens'])
metrics.gauge("llm.cost", usage['total_cost'])
```

## Limitations

- Token estimation is approximate (~4 chars/token heuristic)
- Pricing may change - update `TokenTracker.PRICING` as needed
- Only tracks PromptManager operations, not LLM API calls
- Output tokens are only tracked if you manually call `track_usage()` with output_tokens

## See Also

- `example_token_tracking.py` - Full working example
- `COST_ANALYSIS.md` - Cost optimization strategies
- `README.md` - General PromptManager documentation

