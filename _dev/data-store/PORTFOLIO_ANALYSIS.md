# Portfolio Analysis & Schema Design

## Overview

This document describes the hybrid database architecture for the portfolio management system, combining:
- **PostgreSQL** (relational DB) for structured portfolio, user, and asset data
- **MongoDB** (document DB) for flexible company/stock JSON data

The connection between the two databases is established via the `ticker` symbol, enabling relational integrity in PostgreSQL while maintaining schema flexibility in MongoDB.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│              Application Layer                           │
│         (Portfolio Service/API)                         │
└──────────────┬──────────────────────┬───────────────────┘
               │                      │
       ┌───────▼────────┐    ┌───────▼─────────┐
       │  PostgreSQL    │    │    MongoDB      │
       │  (Relational)  │    │  (Document)     │
       │                │    │                 │
       │ • users        │    │ • companies     │
       │ • portfolios   │    │   collection    │
       │ • assets       │    │   (flexible     │
       │                │    │    JSON)        │
       └───────┬────────┘    └───────┬─────────┘
               │                     │
               └──────────┬──────────┘
                          │
                     (via ticker)
```

## PostgreSQL Schema (Relational Database)

### Database: `trainer_data`

PostgreSQL stores all structured, relational data with ACID guarantees, foreign key constraints, and normalized design.

### Table: `users`

Stores user account information.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
```

**Columns:**
- `id`: Primary key, auto-incrementing
- `username`: Unique username
- `email`: Unique email address
- `password_hash`: Hashed password (use bcrypt/argon2)
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp

### Table: `portfolios`

Stores user portfolios. A user can have multiple portfolios.

```sql
CREATE TABLE portfolios (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, name)
);

CREATE INDEX idx_portfolios_user_id ON portfolios(user_id);
```

**Columns:**
- `id`: Primary key, auto-incrementing
- `user_id`: Foreign key to `users.id` (CASCADE delete)
- `name`: Portfolio name (unique per user)
- `description`: Optional portfolio description
- `created_at`: Portfolio creation timestamp
- `updated_at`: Last update timestamp

**Constraints:**
- One user cannot have two portfolios with the same name
- Deleting a user automatically deletes all their portfolios (CASCADE)

### Table: `assets`

Stores assets (stocks) within portfolios. Links to MongoDB via `ticker`.

```sql
CREATE TABLE assets (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    quantity DECIMAL(15, 4) NOT NULL DEFAULT 0,
    average_cost DECIMAL(15, 4),
    notes TEXT,
    added_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(portfolio_id, ticker)
);

CREATE INDEX idx_assets_portfolio_id ON assets(portfolio_id);
CREATE INDEX idx_assets_ticker ON assets(ticker);
```

**Columns:**
- `id`: Primary key, auto-incrementing
- `portfolio_id`: Foreign key to `portfolios.id` (CASCADE delete)
- `ticker`: Stock ticker symbol (e.g., "AAPL", "MSFT") - **KEY CONNECTION POINT TO MONGODB**
- `quantity`: Number of shares (decimal for fractional shares)
- `average_cost`: Average purchase price per share
- `notes`: Optional notes about the asset
- `added_at`: When asset was added to portfolio
- `updated_at`: Last update timestamp

**Constraints:**
- One portfolio cannot have duplicate tickers (one asset per ticker per portfolio)
- Deleting a portfolio automatically deletes all its assets (CASCADE)

### Connection to MongoDB

The `assets.ticker` field is the **connection point** to MongoDB:

- PostgreSQL `assets.ticker` → MongoDB `companies` collection query by `ticker`
- No foreign key constraint across databases (application-level relationship)
- Query pattern: Use `assets.ticker` to lookup company data in MongoDB

## MongoDB Schema (Document Database)

### Database: `trainer_data`

### Collection: `companies`

Stores flexible JSON company/stock data retrieved from Yahoo Finance or other sources.

**Document Structure:**

```javascript
{
  "key": "company:AAPL",
  "data": {
    "ticker": "AAPL",
    "extractedAt": "2025-01-15T10:30:00.000Z",
    
    // Company fundamentals (current snapshot)
    "valuation": {
      "marketCap": "2.5T",
      "enterpriseValue": "2.45T",
      "trailingPE": "28.5",
      "forwardPE": "26.2",
      "pegRatio": "0.78",
      "priceToSales": "27.06",
      "priceToBook": "44.10",
      "enterpriseValueRevenue": "26.46",
      "enterpriseValueEBITDA": "42.37"
    },
    
    "financials": {
      "revenue": "394.33B",
      "revenuePerShare": "25.45",
      "quarterlyRevenueGrowth": "5.60%",
      "grossProfit": "169.14B",
      "ebitda": "130.54B",
      "netIncome": "99.80B",
      "earningsPerShare": "6.42",
      "quarterlyEarningsGrowth": "13.20%"
    },
    
    "profitability": {
      "profitMargin": "25.31%",
      "operatingMargin": "29.82%",
      "returnOnAssets": "28.45%",
      "returnOnEquity": "172.34%"
    },
    
    // Optional: Historical price data (added when include_historical=true)
    "historical": {
      "period": "1y",
      "interval": "1d",
      "records": 252,
      "data": [
        {
          "date": "2024-01-15",
          "open": 185.50,
          "high": 186.20,
          "low": 185.10,
          "close": 185.85,
          "volume": 52345678,
          "dividends": 0.24,
          "stock_splits": 0
        },
        // ... more historical records
      ]
    }
  },
  "metadata": {
    "source": "yahoo_finance",
    "ticker": "AAPL",
    "extracted_at": "2025-01-15T10:30:00.000Z",
    "has_historical": true  // Flag indicating historical data exists
  },
  "source": "yahoo_finance",
  "stored_at": "2025-01-15T10:30:00.000Z",
  "updated_at": "2025-01-15T10:30:00.000Z",
  "version": 1
}
```

**Key Fields:**
- `key`: Unique document key (format: `"company:{TICKER}"`)
- `data.ticker`: Stock ticker symbol - **CONNECTION POINT FROM POSTGRESQL**
- `data.valuation`: Company valuation metrics
- `data.financials`: Financial metrics
- `data.profitability`: Profitability ratios
- `data.historical`: Optional historical price data (time-series)
- `metadata.ticker`: Duplicate ticker for easier querying
- `metadata.has_historical`: Flag indicating if historical data is present

**Query Pattern:**
```python
# Query MongoDB by ticker (connection from PostgreSQL assets.ticker)
company_result = mongo_store.query({
    "$or": [
        {"data.ticker": ticker},
        {"metadata.ticker": ticker}
    ]
}, sort={"updated_at": -1}, limit=1)
```

## Relationship Pattern

### Connection Flow

```
PostgreSQL                           MongoDB
┌─────────────┐                     ┌──────────────┐
│ assets      │                     │ companies    │
│             │                     │              │
│ id          │                     │ key          │
│ portfolio_id│                     │ data.ticker  │◄──┐
│ ticker ─────┼─────────────────────┼─ metadata    │   │
│ quantity    │    (application-    │   .ticker    │   │
│ avg_cost    │     level join)     │              │   │
└─────────────┘                     └──────────────┘   │
                                                       │
                          Query MongoDB using ticker ──┘
```

### Relationship Characteristics

1. **No Foreign Key Constraint**: Cannot enforce referential integrity across databases
2. **Application-Level Join**: Connection happens in application code
3. **Flexible Schema**: MongoDB documents can evolve without breaking PostgreSQL schema
4. **Ticker as Bridge**: `ticker` symbol is the linking field
5. **Optional Data**: MongoDB company data may not exist for all tickers in assets table

## Design Rationale

### Why PostgreSQL for Portfolios/Assets?

- **ACID Transactions**: Ensure portfolio operations are atomic
- **Referential Integrity**: Foreign keys guarantee data consistency
- **Structured Data**: Users, portfolios, and assets have fixed schemas
- **Complex Queries**: JOINs, aggregations, and constraints
- **Data Integrity**: Cannot delete user with existing portfolios (CASCADE)

### Why MongoDB for Company Data?

- **Flexible Schema**: Company data structure can evolve (add new metrics)
- **Large JSON Documents**: Complex nested structures (valuation, financials, historical)
- **Optional Fields**: Historical data may or may not be present
- **Time-Series Data**: Historical price data fits naturally
- **Schema Evolution**: No migrations needed when adding new fields

### Hybrid Benefits

1. **Best of Both Worlds**: Relational integrity + Schema flexibility
2. **Performance**: Indexed lookups in both databases
3. **Scalability**: Each database optimized for its use case
4. **Separation of Concerns**: Structured data vs. Flexible data
5. **Independent Evolution**: Change MongoDB schema without affecting PostgreSQL

## Query Patterns

### Pattern 1: Get Portfolio with Company Data

```python
# 1. Get assets from PostgreSQL
assets = pg_store.get_portfolio_assets(portfolio_id)

# 2. For each asset, lookup company data in MongoDB
for asset in assets:
    ticker = asset["ticker"]
    
    # Query MongoDB by ticker
    company_result = mongo_store.query(
        {"$or": [
            {"data.ticker": ticker},
            {"metadata.ticker": ticker}
        ]},
        sort={"updated_at": -1},
        limit=1
    )
    
    # Combine PostgreSQL asset + MongoDB company data
    combined = {
        "asset": asset,  # From PostgreSQL
        "company": company_result.items[0].data if company_result.items else None  # From MongoDB
    }
```

### Pattern 2: Calculate Portfolio Value

```python
# 1. Get assets from PostgreSQL (quantity, average_cost)
assets = pg_store.get_portfolio_assets(portfolio_id)

# 2. Get current prices from MongoDB (latest company data)
for asset in assets:
    ticker = asset["ticker"]
    
    # Get latest company data
    company = mongo_store.query({"metadata.ticker": ticker}, sort={"updated_at": -1}, limit=1)
    
    # Extract current price (from valuation or historical data)
    current_price = extract_price(company.data)
    
    # Calculate: market_value = quantity * current_price
    market_value = asset["quantity"] * current_price
```

### Pattern 3: Validate Asset Before Adding

```python
# Before adding asset to PostgreSQL, verify ticker exists in MongoDB
ticker = "AAPL"

company_result = mongo_store.query(
    {"$or": [
        {"data.ticker": ticker},
        {"metadata.ticker": ticker}
    ]},
    limit=1
)

if not company_result.items:
    raise ValueError(f"Ticker {ticker} not found in company database")

# Now safe to add to PostgreSQL
pg_store.add_asset(portfolio_id, ticker, quantity, average_cost)
```

## Data Flow

### Adding an Asset to Portfolio

```
1. User selects ticker (e.g., "AAPL")
   ↓
2. Application queries MongoDB to verify ticker exists
   ↓
3. If exists, fetch company data (optional: for display)
   ↓
4. User enters quantity and average_cost
   ↓
5. Insert into PostgreSQL: assets table
   (portfolio_id, ticker, quantity, average_cost)
   ↓
6. Asset linked to MongoDB via ticker (no explicit FK)
```

### Loading Portfolio with Company Data

```
1. Query PostgreSQL: Get all assets for portfolio_id
   SELECT * FROM assets WHERE portfolio_id = ?
   ↓
2. For each asset, extract ticker
   ↓
3. Query MongoDB: Get company data for each ticker
   db.companies.find({$or: [{data.ticker: "AAPL"}, {metadata.ticker: "AAPL"}]})
   ↓
4. Combine results in application layer
   ↓
5. Return combined portfolio view
```

## Indexes

### PostgreSQL Indexes

```sql
-- Users
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- Portfolios
CREATE INDEX idx_portfolios_user_id ON portfolios(user_id);

-- Assets
CREATE INDEX idx_assets_portfolio_id ON assets(portfolio_id);
CREATE INDEX idx_assets_ticker ON assets(ticker);  -- Important for MongoDB lookups
```

### MongoDB Indexes

```javascript
// Companies collection
db.companies.createIndex({"key": 1}, {unique: true});
db.companies.createIndex({"data.ticker": 1});
db.companies.createIndex({"metadata.ticker": 1});  // Important for PostgreSQL lookups
db.companies.createIndex({"source": 1});
db.companies.createIndex({"stored_at": 1});
db.companies.createIndex({"updated_at": -1});  // For getting latest data
```

## Implementation Considerations

### 1. Ticker Consistency

- Ensure tickers are uppercase in both databases: `"AAPL"` not `"aapl"`
- Normalize ticker format when storing in PostgreSQL
- Use same normalization when querying MongoDB

### 2. Missing Company Data

- Handle case where PostgreSQL asset has ticker not in MongoDB
- Return `null` for company data, but still show asset with quantity/cost
- Provide mechanism to fetch missing company data (trigger data-retriever)

### 3. Data Freshness

- MongoDB company data may be stale
- Consider TTL or refresh strategy for company data
- Use `updated_at` to determine data freshness

### 4. Historical Data

- Historical data is optional in MongoDB (may not exist)
- Check `metadata.has_historical` flag before accessing
- Gracefully handle missing historical data in queries

### 5. Transaction Boundaries

- PostgreSQL operations can use transactions
- MongoDB operations are separate (no cross-database transactions)
- Consider eventual consistency for portfolio calculations

### 6. Error Handling

- Handle MongoDB connection failures gracefully
- Fallback to PostgreSQL-only data if MongoDB unavailable
- Log warnings when company data not found

## Future Enhancements

### Potential Additions

1. **Asset Transactions Table**: Track buy/sell history
   ```sql
   CREATE TABLE asset_transactions (
       id SERIAL PRIMARY KEY,
       asset_id INTEGER REFERENCES assets(id),
       transaction_type VARCHAR(10),  -- 'buy' or 'sell'
       quantity DECIMAL(15, 4),
       price DECIMAL(15, 4),
       transaction_date TIMESTAMP
   );
   ```

2. **Portfolio Performance Tracking**: Store calculated metrics
   ```sql
   CREATE TABLE portfolio_performance (
       id SERIAL PRIMARY KEY,
       portfolio_id INTEGER REFERENCES portfolios(id),
       calculated_at TIMESTAMP,
       total_value DECIMAL(15, 2),
       total_cost DECIMAL(15, 2),
       gain_loss DECIMAL(15, 2)
   );
   ```

3. **Watchlists**: Track stocks of interest (no quantity)
   ```sql
   CREATE TABLE watchlists (
       id SERIAL PRIMARY KEY,
       user_id INTEGER REFERENCES users(id),
       ticker VARCHAR(10),
       added_at TIMESTAMP
   );
   ```

## Summary

This hybrid architecture provides:

- **PostgreSQL**: Structured, relational data with integrity constraints (users, portfolios, assets)
- **MongoDB**: Flexible, document-based company/stock data (JSON with evolving schema)
- **Connection**: Via `ticker` field (application-level relationship)
- **Benefits**: ACID transactions + Schema flexibility + Independent evolution

The design separates concerns appropriately:
- **What belongs in PostgreSQL**: User accounts, portfolio structure, asset holdings (quantity, cost)
- **What belongs in MongoDB**: Company fundamentals, financial metrics, historical price data

This enables building a robust portfolio management system that can handle structured portfolio operations while maintaining flexibility for evolving stock data structures.
