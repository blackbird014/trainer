# Real-World Usage Example

This document explains how to use PromptManager with your actual project files.

## File Locations

### JSON Data Files
**Location**: `output/json/`

These contain the actual stock/company financial data scraped from Yahoo Finance.

**Available files**:
- `example_nvda_data.json` - Single company example
- `stock_data_20251119_134901.json` - Multiple companies (array format)
- `stock_data_20251121_122508.json` - Multiple companies (array format)

**Format**: JSON array or object with ticker, valuation, financials, profitability metrics

### Context Files (Domain Knowledge)
**Location**: `information/context/`

These are large markdown files containing domain knowledge and background information.

**Available contexts**:
- `biotech/01-introduction.md` - Biotech investment pipeline overview
- `biotech/molecular-biology-foundations.md` - Molecular biology foundations
- `economical-context.md` - Economic environment assumptions
- `01-introduction.md` - General introduction

**Purpose**: Provide domain knowledge that doesn't change frequently (can be cached)

### Instruction Files (Prompts/Templates)
**Location**: `information/instructions/`

These are prompt templates that define the structure and requirements for analysis.

**Available instructions**:
- `01-instruction.md` - Basic instruction template
- `prompt-for-biotech-single-company.md` - Biotech company analysis template
- `company-metrics-table-prompt.md` - Metrics table generation template

**Purpose**: Define what analysis to perform and how to structure the output

## Workflow

The typical workflow is:

```
1. Load Context Files (domain knowledge)
   ↓
2. Load Instruction Template (what to do)
   ↓
3. Load JSON Data (actual company metrics)
   ↓
4. Fill Template Variables (inject data into instruction)
   ↓
5. Compose Final Prompt (contexts + filled instruction)
   ↓
6. Send to LLM for analysis
```

## Running the Example

```bash
# From the prompt-manager directory
source .venv/bin/activate
python example_real_usage.py
```

This will:
1. Load 3 context files (~17KB of domain knowledge)
2. Load the instruction template
3. Load JSON data from `output/json/`
4. Compose everything into a final prompt (~18KB total)
5. Save the result to `example_output.md`

## Example Output

The example creates a prompt that:
- **Starts with contexts**: Provides biotech domain knowledge
- **Includes instruction**: Defines what analysis to perform
- **Contains data**: Actual company metrics from JSON

This composed prompt can then be sent to an LLM (like GPT-4) to generate the actual analysis report.

## Key Benefits

1. **Separation of Concerns**:
   - Contexts = Domain knowledge (rarely changes)
   - Instructions = Analysis structure (changes per use case)
   - Data = Company metrics (changes per company)

2. **Caching**: Large contexts can be cached to avoid reloading

3. **Reusability**: Same contexts can be used with different instructions/data

4. **Maintainability**: Update contexts/instructions independently

## Customizing the Example

To use different files, modify `example_real_usage.py`:

```python
# Change context files
context_files = [
    "biotech/01-introduction.md",
    "your-custom-context.md"
]

# Change instruction file
instruction_path = PROJECT_ROOT / "information" / "instructions" / "your-instruction.md"

# Change JSON file
json_file = PROJECT_ROOT / "output" / "json" / "your-data.json"
```

## Next Steps

1. Review `example_output.md` to see the composed prompt
2. Modify the example to use your specific contexts/instructions
3. Integrate with an LLM provider (Phase 2) to actually execute the prompt
4. Use format converter (Phase 4) to convert LLM output to HTML/PDF

