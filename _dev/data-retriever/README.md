# Data Retriever

A Python module providing a unified interface for retrieving data from various sources.

## Features

- **Unified API**: Single interface for different data sources
- **Multiple Sources**: Yahoo Finance, SEC filings, REST APIs, databases, files
- **Caching**: Built-in caching to avoid redundant requests
- **Schema Validation**: Validate retrieved data against schemas
- **Rate Limiting**: Configurable rate limiting per retriever
- **Error Handling**: Graceful error handling with detailed error messages
- **Prometheus Metrics**: Built-in metrics for monitoring

## Installation

### Basic Installation

```bash
pip install -e .
```

### With Optional Dependencies

```bash
# Browser automation (for Yahoo Finance scraping)
pip install -e ".[browser]"

# Database support
pip install -e ".[database]"

# SEC filings support
pip install -e ".[sec]"

# All optional dependencies
pip install -e ".[all]"
```

## Quick Start

### File Retriever

```python
from data_retriever import FileRetriever

retriever = FileRetriever(base_path="./data")
result = retriever.retrieve({"path": "stock_data.json"})

if result.success:
    print(result.data["content"])
```

### API Retriever

```python
from data_retriever import APIRetriever

retriever = APIRetriever(base_url="https://api.example.com")
result = retriever.retrieve({
    "url": "/endpoint",
    "method": "GET",
    "params": {"ticker": "AAPL"}
})

if result.success:
    print(result.data["data"])
```

### With Caching

```python
from data_retriever import FileRetriever, DataCache

cache = DataCache(default_ttl=3600)  # 1 hour cache
retriever = FileRetriever(cache=cache)

# First call - fetches from file
result1 = retriever.retrieve_with_cache({"path": "data.json"})

# Second call - uses cache
result2 = retriever.retrieve_with_cache({"path": "data.json"})
```

### Yahoo Finance Retriever

```python
from data_retriever import YahooFinanceRetriever

retriever = YahooFinanceRetriever(use_browser=False)  # Use API
result = retriever.retrieve({"ticker": "AAPL"})

if result.success:
    print(result.data)
```

## API Service

The module includes a FastAPI service for exposing data retrieval via REST API:

```bash
cd _dev/data-retriever
python api_service.py
```

The service runs on port 8003 (configurable via `PORT` environment variable) and provides:

- `GET /` - API information
- `GET /health` - Health check
- `GET /sources` - List available data sources
- `POST /retrieve` - Retrieve data from a source
- `GET /metrics` - Prometheus metrics endpoint

### Example API Usage

```bash
# List available sources
curl http://localhost:8003/sources

# Retrieve data from file source
curl -X POST http://localhost:8003/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "source": "file",
    "query": {"path": "data.json"}
  }'

# Retrieve data from API source
curl -X POST http://localhost:8003/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "source": "api",
    "query": {
      "url": "https://api.github.com/repos/octocat/Hello-World"
    }
  }'
```

## Prometheus Metrics

The module exposes Prometheus metrics at `/metrics` endpoint:

- `data_retriever_operations_total` - Total retrieval operations (by source, status)
- `data_retriever_operation_duration_seconds` - Operation duration histogram (by source)
- `data_retriever_cache_hits_total` - Cache hits (by source)
- `data_retriever_cache_misses_total` - Cache misses (by source)
- `data_retriever_errors_total` - Total errors (by source, error_type)
- `data_retriever_data_size_bytes` - Retrieved data size histogram (by source)
- `data_retriever_active_operations` - Currently active operations (by source)

### Monitoring Setup

1. **Start the API service**:
   ```bash
   cd _dev/data-retriever
   python api_service.py
   ```

2. **Configure Prometheus** (already configured in centralized monitoring):
   The centralized monitoring at `_dev/monitoring/` is already configured to scrape data-retriever on port 8003.

3. **View Grafana Dashboard**:
   - Start centralized monitoring: `cd _dev/monitoring && docker-compose up -d`
   - Access Grafana: http://localhost:3000
   - Navigate to "Data Retriever Dashboard"

## API Reference

### DataRetriever (Base Class)

Abstract base class for all retrievers.

```python
class DataRetriever(ABC):
    def retrieve(self, query: Dict[str, Any]) -> RetrievalResult
    def get_schema(self) -> Schema
    def retrieve_with_cache(self, query: Dict[str, Any]) -> RetrievalResult
```

### RetrievalResult

Result of a data retrieval operation.

```python
@dataclass
class RetrievalResult:
    data: Dict[str, Any]          # Retrieved data
    source: str                    # Source name
    retrieved_at: datetime         # Timestamp
    metadata: Dict[str, Any]        # Additional metadata
    success: bool                  # Success flag
    error: Optional[str]           # Error message if failed
```

### FileRetriever

Retrieve data from local filesystem.

**Query Parameters:**
- `path`: File path (required)
- `format`: File format ('json', 'text', 'auto')

**Example:**
```python
retriever = FileRetriever(base_path="./data")
result = retriever.retrieve({"path": "file.json", "format": "json"})
```

### APIRetriever

Generic REST API retriever.

**Query Parameters:**
- `url`: API endpoint URL (required)
- `method`: HTTP method (default: 'GET')
- `params`: Query parameters
- `data`: Request body data
- `headers`: Additional headers
- `timeout`: Request timeout

**Example:**
```python
retriever = APIRetriever(base_url="https://api.example.com")
result = retriever.retrieve({
    "url": "/endpoint",
    "method": "POST",
    "data": {"key": "value"}
})
```

### YahooFinanceRetriever

Yahoo Finance stock data retriever.

**Query Parameters:**
- `ticker`: Stock ticker symbol (required)
- `tickers`: List of ticker symbols (for batch)
- `metrics`: List of specific metrics to retrieve

**Example:**
```python
retriever = YahooFinanceRetriever()
result = retriever.retrieve({"ticker": "AAPL"})
```

### SECRetriever

SEC EDGAR database retriever.

**Query Parameters:**
- `ticker`: Company ticker symbol (required)
- `filing_type`: Type of filing (10-K, 10-Q, etc.)
- `year`: Filing year
- `limit`: Maximum number of filings

**Example:**
```python
retriever = SECRetriever()
result = retriever.retrieve({
    "ticker": "AAPL",
    "filing_type": "10-K",
    "year": 2023
})
```

### DatabaseRetriever

SQL database retriever.

**Query Parameters:**
- `sql`: SQL query string (required)
- `params`: Query parameters for parameterized queries

**Example:**
```python
retriever = DatabaseRetriever(connection_string="sqlite:///data.db")
result = retriever.retrieve({
    "sql": "SELECT * FROM stocks WHERE ticker = :ticker",
    "params": {"ticker": "AAPL"}
})
```

## Caching

The `DataCache` class provides in-memory caching with TTL support.

```python
from data_retriever import DataCache

cache = DataCache(
    default_ttl=3600,  # Default TTL in seconds
    max_size=1000      # Maximum cached items
)

# Set with custom TTL
cache.set("key", {"data": "value"}, ttl=1800)

# Get from cache
data = cache.get("key")

# Clear cache
cache.clear()
```

## Schema Validation

Schemas define the expected structure of retrieved data.

```python
from data_retriever import Schema, Field, FieldType

schema = Schema(
    name="stock_data",
    fields=[
        Field("ticker", FieldType.STRING, required=True),
        Field("price", FieldType.FLOAT, required=True),
        Field("volume", FieldType.INTEGER, required=False),
    ]
)

# Validate data
is_valid, errors = schema.validate({
    "ticker": "AAPL",
    "price": 150.0
})
```

## Rate Limiting

Configure rate limiting to avoid overwhelming data sources.

```python
retriever = APIRetriever(rate_limit=10.0)  # 10 requests per second
```

## Error Handling

All retrievers return `RetrievalResult` objects with success flags and error messages.

```python
result = retriever.retrieve(query)

if result.success:
    # Use result.data
    process_data(result.data)
else:
    # Handle error
    print(f"Error: {result.error}")
```

## Development

### Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in development mode
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

Or use the test runner:

```bash
./run_tests.sh
```

### Run Tests with Coverage

```bash
pytest --cov=data_retriever --cov-report=html
```

### Format Code

```bash
black src/
```

### Lint Code

```bash
ruff check src/
```

## Package Structure

```
data-retriever/
├── src/
│   ├── data_retriever/
│   │   ├── __init__.py
│   │   ├── base.py              # Base abstraction
│   │   ├── schema.py            # Schema definitions
│   │   ├── cache.py             # Caching system
│   │   ├── metrics.py           # Prometheus metrics
│   │   └── retrievers/
│   │       ├── __init__.py
│   │       ├── file_retriever.py
│   │       ├── api_retriever.py
│   │       ├── yahoo_finance_retriever.py
│   │       ├── sec_retriever.py
│   │       └── database_retriever.py
│   └── tests/
├── api_service.py               # FastAPI service
├── pyproject.toml
└── README.md
```

## Dependencies

### Core Dependencies
- `requests>=2.31.0` - HTTP library
- `pandas>=2.0.0` - Data manipulation
- `prometheus-client>=0.19.0` - Metrics collection
- `fastapi>=0.104.0` - API framework
- `uvicorn[standard]>=0.24.0` - ASGI server

### Optional Dependencies
- `selenium>=4.15.0` - Browser automation (Yahoo Finance)
- `playwright>=1.40.0` - Browser automation (alternative)
- `sqlalchemy>=2.0.0` - Database support
- `sec-edgar-downloader>=4.0.0` - SEC filings

## License

MIT
