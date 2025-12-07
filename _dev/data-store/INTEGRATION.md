# Data-Store Integration Guide

This document explains how `data-store` integrates with other modules in the trainer project.

## Architecture Overview

### Before Data-Store (Direct Integration)
```
data-retriever → prompt-manager → llm-provider → format-converter
```

### After Data-Store (Decoupled Architecture)
```
data-retriever → data-store → prompt-manager (queries store)
                              ↓
                         llm-provider
                              ↓
                         format-converter → data-store (stores outputs)
```

## Integration Points

### 1. Data Retriever → Data Store

**Pattern**: Data retriever stores results automatically in data-store.

```python
from data_store import create_store
from data_retriever import FileRetriever

# Initialize store
store = create_store("mongodb", connection_string="mongodb://localhost:27017")

# Initialize retriever (would integrate store automatically)
retriever = FileRetriever(base_path="data/")
result = retriever.retrieve({"path": "file.json"})

# Store in data-store
store.store(
    key="retrieved:file.json",
    data=result.data,
    metadata={"source": "file_retriever"}
)
```

### 2. Prompt Manager → Data Store

**Pattern**: Prompt manager queries data-store instead of calling data-retriever directly.

```python
from data_store import create_store
from prompt_manager import PromptManager

# Initialize store
store = create_store("mongodb", connection_string="mongodb://localhost:27017")

# Initialize prompt manager with data-store
prompt_manager = PromptManager(
    context_dir="context/",
    data_store=store  # Pass store to prompt manager
)

# Prompt manager queries store internally
# data = store.query({"source": "yahoo_finance", "ticker": "AAPL"})
```

### 3. Format Converter → Data Store

**Pattern**: Format converter stores formatted outputs in data-store.

```python
from data_store import create_store
from format_converter import FormatConverter

# Initialize store
store = create_store("mongodb", connection_string="mongodb://localhost:27017")

# Convert format
converter = FormatConverter()
html = converter.convert(markdown, "markdown", "html")

# Store formatted output
store.store(
    key="formatted:report:html",
    data={"html": html, "markdown": markdown},
    metadata={"source": "format_converter", "format": "html"}
)
```

## Complete Integration Example

See `examples/integration_with_modules.py` for a complete example showing:
- Data retrieval and storage
- Querying stored data
- Using stored data in format conversion
- Storing formatted outputs

## Benefits of Data-Store Integration

1. **Decoupling**: Modules don't need to know about data sources
2. **Persistence**: Data survives restarts
3. **Multi-Consumer**: Multiple modules can access same data
4. **Analytics**: Query and analyze stored data
5. **ETL Support**: Enable batch processing and transformations

## Updated Module Dependencies

```
prompt-manager
└── data-store (for querying stored data)

data-retriever
└── data-store (for automatic persistence)

format-converter
└── data-store (optional, for storing outputs)

data-store (core module, no dependencies on other trainer modules)
```

## Migration Guide

### Old Pattern (Direct)
```python
# Old: Direct retrieval
data = data_retriever.retrieve(query)
prompt_manager.use_data(data)
```

### New Pattern (With Data-Store)
```python
# New: Store first, then query
data_retriever.retrieve(query)  # Automatically stores
data = data_store.query(filters)  # Query from store
prompt_manager.use_data(data)
```

## Examples

- `examples/integration_with_modules.py` - Basic integration
- `examples/mongodb_json_storage.py` - MongoDB-specific examples
- `examples/etl/simple_pipeline.py` - ETL pipeline example

