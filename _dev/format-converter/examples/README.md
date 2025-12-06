# Format Converter Examples

This directory contains example scripts demonstrating format-converter usage.

## Examples

### basic_usage.py

Basic usage examples:
- Markdown to HTML conversion
- JSON to Markdown conversion
- Auto-detection
- JSON extraction from text

**Run:**
```bash
python examples/basic_usage.py
```

### integration_all_modules.py

Complete integration example connecting all modules:
- prompt-manager
- prompt-security
- llm-provider
- data-retriever
- format-converter

Demonstrates the full workflow:
1. Load data from data-retriever
2. Create prompt with prompt-manager
3. Execute with llm-provider
4. Convert output with format-converter

**Run:**
```bash
python examples/integration_all_modules.py
```

**Prerequisites:**
- All modules installed
- Data file available at `../../output/json/stock_data_20251121_122508.json`
- Optional: `OPENAI_API_KEY` environment variable for LLM calls

## Usage

All examples can be run directly:

```bash
cd _dev/format-converter
python examples/basic_usage.py
python examples/integration_all_modules.py
```

