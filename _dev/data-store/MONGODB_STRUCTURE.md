# MongoDB Structure Explained

## How MongoDB Organizes Data

### Database → Collections → Documents

MongoDB uses a **hierarchical structure**:

```
Database: trainer_data
  │
  ├── Collection: seed_companies      (like a SQL table)
  │   └── Documents: {ticker: "AAPL", company: "Apple Inc.", ...}
  │
  ├── Collection: scraped_metrics     (like a SQL table)
  │   └── Documents: {ticker: "AAPL", price: 150.25, ...}
  │
  └── Collection: prompt_runs        (like a SQL table)
      └── Documents: {ticker: "AAPL", prompt: "...", response: "..."}
```

## Key Concepts

### 1. **Database** (`trainer_data`)
- Top-level container
- Contains multiple collections
- Similar to a "database" in SQL

### 2. **Collections** (like SQL tables)
- **Separate storage units** for different data types
- Each collection can have a **different schema** (flexible JSON)
- Collections are **independent** - queries don't mix them
- Examples: `seed_companies`, `scraped_metrics`, `prompt_runs`

### 3. **Documents** (like SQL rows)
- Individual JSON objects stored in collections
- Each document has a unique `key` (like a primary key)
- Documents can have different fields (flexible schema)

## Current Collections in Our Setup

Based on the stock mini-app specification:

| Collection | Purpose | Data Type |
|------------|---------|-----------|
| `seed_companies` | 100 fake companies from bulk insert | Company metadata (ticker, name, market cap, etc.) |
| `scraped_metrics` | Yahoo Finance scraped data | Stock metrics (price, volume, P/E ratio, etc.) |
| `prompt_runs` | LLM prompt + responses | Prompt analysis results (prompt text, LLM response, rendered HTML) |
| `data_store` | General purpose (default) | Any other data |
| `etl_data` | ETL pipeline results | Processed data from ETL |

## How data-store Uses Collections

### Creating Stores with Different Collections

```python
from data_store import create_store

# Collection 1: Companies
companies_store = create_store(
    "mongodb",
    connection_string="mongodb://localhost:27017",
    database="trainer_data",
    collection="seed_companies"  # ← Specify collection name
)

# Collection 2: Metrics
metrics_store = create_store(
    "mongodb",
    connection_string="mongodb://localhost:27017",
    database="trainer_data",
    collection="scraped_metrics"  # ← Different collection
)

# Collection 3: Prompts
prompts_store = create_store(
    "mongodb",
    connection_string="mongodb://localhost:27017",
    database="trainer_data",
    collection="prompt_runs"  # ← Different collection
)
```

### Data Isolation

**Important**: Each collection is **completely separate**:

```python
# Store in companies collection
companies_store.store("company:AAPL", {"ticker": "AAPL", "name": "Apple"})

# Query companies collection
result = companies_store.query({})  # Only finds data in seed_companies

# Query metrics collection (different store)
result2 = metrics_store.query({})  # Only finds data in scraped_metrics
# result2 will NOT include the company data above!
```

## Benefits of Separate Collections

### ✅ **Organization**
- Clear separation by data type
- Easy to understand what data is where
- Logical grouping (companies, metrics, prompts)

### ✅ **Performance**
- Each collection can have **separate indexes**
- Queries are faster (only search relevant collection)
- Can optimize indexes per collection type

### ✅ **Scalability**
- Can **shard collections independently**
- Can move collections to different servers
- Can set different TTL (time-to-live) per collection

### ✅ **Management**
- Backup/restore per collection
- Can drop a collection without affecting others
- Can set different access permissions per collection

## Example: Stock Mini-App Structure

### Step 1: Seed Companies (Collection: `seed_companies`)
```python
companies_store.store(
    key="company:AAPL",
    data={
        "ticker": "AAPL",
        "company": "Apple Inc.",
        "market_cap": 2500000000000,
        "sector": "Technology"
    },
    metadata={"source": "seed_data", "type": "company"}
)
```

### Step 2: Scrape Metrics (Collection: `scraped_metrics`)
```python
metrics_store.store(
    key="metrics:AAPL:2024-01-01",
    data={
        "ticker": "AAPL",
        "price": 150.25,
        "volume": 1000000,
        "pe_ratio": 28.5
    },
    metadata={"source": "yahoo_finance", "date": "2024-01-01"}
)
```

### Step 3: Prompt Analysis (Collection: `prompt_runs`)
```python
prompts_store.store(
    key="prompt:AAPL:2024-01-01",
    data={
        "ticker": "AAPL",
        "prompt": "Analyze Apple's stock performance",
        "llm_response": "...",
        "rendered_html": "<html>...</html>"
    },
    metadata={"source": "prompt_manager", "llm_provider": "mock"}
)
```

## Querying Collections

### Query Within a Collection
```python
# Find all companies with market cap > 1B
result = companies_store.query(
    {"data.market_cap": {"$gt": 1000000000}}
)

# Find all metrics for a ticker
result = metrics_store.query(
    {"data.ticker": "AAPL"}
)
```

### Cross-Collection Queries
**Note**: MongoDB doesn't support JOINs like SQL. To combine data from multiple collections, you need to:

1. Query each collection separately
2. Combine results in application code
3. Or use MongoDB aggregation pipelines (advanced)

Example:
```python
# Get company info
company = companies_store.retrieve("company:AAPL")

# Get latest metrics
metrics = metrics_store.query(
    {"data.ticker": "AAPL"},
    sort={"stored_at": -1},  # Most recent first
    limit=1
)

# Combine in application
combined = {
    "company": company.data,
    "metrics": metrics.items[0].data if metrics.items else None
}
```

## Viewing Collections in MongoDB

### Using MongoDB Shell
```bash
docker exec mongodb mongosh trainer_data

# List all collections
show collections

# View documents in a collection
db.seed_companies.find().pretty()

# Count documents
db.seed_companies.countDocuments({})

# Query specific documents
db.scraped_metrics.find({"data.ticker": "AAPL"}).pretty()
```

### Using MongoDB Compass (GUI)
1. Download: https://www.mongodb.com/try/download/compass
2. Connect to: `mongodb://localhost:27017`
3. Browse database: `trainer_data`
4. View collections: `seed_companies`, `scraped_metrics`, `prompt_runs`

## Summary

**MongoDB Structure:**
- ✅ **Database** (`trainer_data`) contains multiple **Collections**
- ✅ **Collections** are separate (like SQL tables)
- ✅ Each collection stores **Documents** (JSON objects)
- ✅ Collections can have **different schemas** (flexible)

**For Stock Mini-App:**
- ✅ Use **separate collections** for different data types
- ✅ `seed_companies` → Company metadata
- ✅ `scraped_metrics` → Yahoo Finance data
- ✅ `prompt_runs` → LLM prompt results
- ✅ Each collection is **independent** and **optimized** for its purpose

**Best Practice:**
- Use **one collection per logical data type**
- Keep related data together in the same collection
- Use metadata to add additional context
- Index frequently queried fields per collection

