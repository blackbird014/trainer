# Data Store Module

Centralized data persistence layer that decouples data retrieval from data consumption, enabling ETL pipelines, analytics, and transparent data source abstraction.

## Features

- **Multiple Storage Backends**: Support for MongoDB, PostgreSQL, SQLite, and Redis
- **Unified API**: Consistent interface regardless of backend
- **Query Interface**: Flexible querying with filters, sorting, and pagination
- **Analytics Support**: Aggregation pipelines, counting, and distinct values
- **TTL Support**: Automatic expiration of stale data
- **Data Versioning**: Track changes over time
- **Prometheus Metrics**: Built-in monitoring and observability
- **FastAPI Service**: REST API for remote access

## Installation

```bash
# Basic installation
pip install trainer-data-store

# With specific backend support
pip install trainer-data-store[mongodb]      # MongoDB support
pip install trainer-data-store[postgresql]   # PostgreSQL support
pip install trainer-data-store[redis]       # Redis support
pip install trainer-data-store[all]          # All backends
```

## Quick Start

### SQLite (Development)

```python
from data_store import create_store

# Create SQLite store (zero configuration)
store = create_store("sqlite", database_path="data/trainer.db")

# Store data
key = store.store(
    key="stock:AAPL",
    data={"price": 150.25, "volume": 1000000},
    metadata={"source": "yahoo_finance"}
)

# Retrieve data
stored = store.retrieve("stock:AAPL")
print(stored.data)

# Query data
result = store.query({"source": "yahoo_finance"})
print(f"Found {result.total} items")
```

### MongoDB (Production)

```python
from data_store import create_store

# Create MongoDB store
store = create_store(
    "mongodb",
    connection_string="mongodb://localhost:27017",
    database="trainer_data"
)

# Store and retrieve
store.store("key", {"data": "value"})
stored = store.retrieve("key")
```

## Storage Backends

### SQLiteStore
- **Use Case**: Development, small-scale deployments
- **Pros**: Zero configuration, file-based, perfect for local development
- **Cons**: Limited concurrency, not ideal for high write loads

### MongoDBStore
- **Use Case**: Production deployments with diverse data types
- **Pros**: Flexible schema, JSON-like documents, excellent for varied data types
- **Cons**: More operational overhead, memory usage
- **Requires**: `pip install trainer-data-store[mongodb]`

### PostgreSQLStore
- **Use Case**: Structured data with ACID requirements
- **Pros**: ACID compliance, JSONB support, mature ecosystem
- **Cons**: Schema changes can be heavier
- **Requires**: `pip install trainer-data-store[postgresql]`

### RedisStore
- **Use Case**: Caching and high-performance scenarios
- **Pros**: Very fast, pub/sub support, TTL built-in
- **Cons**: In-memory only, limited persistence
- **Requires**: `pip install trainer-data-store[redis]`

## API Reference

### Core Methods

#### `store(key, data, metadata=None, ttl=None)`
Store data with a unique key.

```python
key = store.store(
    key="user:123",
    data={"name": "John"},
    metadata={"source": "api"},
    ttl=3600  # Expires in 1 hour
)
```

#### `retrieve(key)`
Retrieve data by key.

```python
stored = store.retrieve("user:123")
if stored:
    print(stored.data)
    print(stored.metadata)
    print(stored.updated_at)
```

#### `query(filters, limit=None, sort=None, offset=0)`
Query data by filters.

```python
result = store.query(
    filters={"source": "yahoo_finance"},
    limit=10,
    sort={"updated_at": -1},  # -1 for desc, 1 for asc
    offset=0
)

for item in result.items:
    print(item.data)
```

#### `update(key, data, metadata=None)`
Update existing data.

```python
success = store.update("user:123", {"name": "Jane"})
```

#### `delete(key)`
Delete data by key.

```python
success = store.delete("user:123")
```

#### `exists(key)`
Check if key exists.

```python
if store.exists("user:123"):
    print("Key exists")
```

#### `get_freshness(key)`
Get last update time.

```python
freshness = store.get_freshness("user:123")
if freshness:
    age = datetime.now() - freshness
    print(f"Data is {age.total_seconds()} seconds old")
```

### Analytics Methods

#### `count(filters)`
Count items matching filters.

```python
count = store.count({"source": "yahoo_finance"})
```

#### `distinct(field, filters=None)`
Get distinct values for a field.

```python
tickers = store.distinct("ticker", {"source": "yahoo_finance"})
```

#### `aggregate(pipeline)` (MongoDB only)
Run aggregation pipeline.

```python
pipeline = [
    {"$match": {"source": "yahoo_finance"}},
    {"$group": {"_id": "$source", "count": {"$sum": 1}}}
]
result = store.aggregate(pipeline)
```

### Bulk Operations

#### `bulk_store(items)`
Store multiple items at once.

```python
items = [
    {"key": "key1", "data": {"value": 1}},
    {"key": "key2", "data": {"value": 2}},
]
result = store.bulk_store(items)
print(f"Loaded {result.records_loaded} items")
```

## FastAPI Service

### Recommended: Using run_api.sh (Automatic venv)

```bash
cd _dev/data-store
./run_api.sh
```

This script automatically:
- Activates `venv` or `.venv` if present (no manual activation needed)
- Shows backend configuration (MongoDB, SQLite, etc.)
- Starts the API service

### Alternative: Direct Python

```bash
cd _dev/data-store
python api_service.py
```

**Note**: If you have a `venv` in the module directory, activate it first:
```bash
source venv/bin/activate  # or source .venv/bin/activate
python api_service.py
```

The service runs on port 8007 by default (configurable via `PORT` environment variable).

### API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /store` - Store data
- `GET /retrieve/{key}` - Retrieve data
- `PUT /update/{key}` - Update data
- `DELETE /delete/{key}` - Delete data
- `GET /exists/{key}` - Check if key exists
- `POST /query` - Query data
- `POST /bulk_store` - Bulk store
- `POST /count` - Count items
- `GET /distinct/{field}` - Get distinct values
- `GET /metrics` - Prometheus metrics

## Configuration

### Environment Variables

```bash
# Backend selection
DATA_STORE_BACKEND=sqlite  # or mongodb, postgresql, redis

# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=trainer_data
MONGODB_COLLECTION=data_store

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=trainer_data
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# SQLite
SQLITE_DATABASE_PATH=data/trainer.db
```

### Programmatic Configuration

```python
from data_store.config import StoreConfig
from data_store import create_store

config = StoreConfig({
    "backend": "mongodb",
    "config": {
        "connection_string": "mongodb://localhost:27017",
        "database": "trainer_data"
    }
})

store = create_store(config.backend, **config.config)
```

## Prometheus Metrics

The module exposes Prometheus metrics:

- `data_store_operations_total` - Total operations by type and status
- `data_store_operation_duration_seconds` - Operation duration
- `data_store_errors_total` - Error counts by type
- `data_store_data_size_bytes` - Data size distribution
- `data_store_items_total` - Total items in store
- `data_store_active_operations` - Currently active operations

## Integration with Other Modules

### Data Retriever Integration

```python
from data_store import create_store
from data_retriever import YahooFinanceRetriever

store = create_store("mongodb", connection_string="mongodb://localhost:27017")
retriever = YahooFinanceRetriever(data_store=store)

# Data automatically stored when retrieved
result = retriever.retrieve({"ticker": "AAPL"})
# Data stored with key: "yahoo_finance:AAPL:20240101"
```

### Prompt Manager Integration

```python
from data_store import create_store
from prompt_manager import PromptManager

store = create_store("mongodb", connection_string="mongodb://localhost:27017")
prompt_manager = PromptManager(data_store=store)

# Query stored data instead of direct retrieval
data = store.query({"source": "yahoo_finance", "ticker": "AAPL"})
```

## Testing

Run tests:

```bash
cd _dev/data-store
./run_tests.sh
```

Or with pytest:

```bash
pytest tests/
```

## Examples

See `examples/basic_usage.py` for comprehensive examples.

## License

MIT

