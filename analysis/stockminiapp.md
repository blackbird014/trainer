# Stock Mini App - Specification Draft (Review Before Implementation)

## Goal
Draft a usage demo (mini‑app spec) that reuses existing modules (data-store, data-retriever, prompt-manager, prompt-security, llm-provider, format-converter) with the already-defined MongoDB Docker instance. This is a specification only; no new mini-app code or new services/endpoints are to be implemented here.

## High-Level Capabilities
1) Seed test data into MongoDB (100 fake companies per request). Trigger should call an existing data-store API/utility that supports insert/bulk-insert (or a small data-store endpoint for this purpose if already provided); if not present, we’ll add this call to data-store rather than creating a separate app-specific service.  
2) Web admin action to scrape Yahoo Finance for given tickers (no LLM), routed through the existing data-retriever service and its `YahooFinanceRetriever` REST API. Store results in MongoDB via data-store.  
3) Web UI flow to run a prompt-driven analysis for a ticker (uses prompt-manager + prompt-security + llm-provider **mock only for first iteration; design stays pluggable to later point to Bedrock or other backends**). Persist prompt + response to MongoDB; render HTML via format-converter; keep MD/JSON variants.  
4) Optional periodic job to materialize MD/HTML/JSON versions (no LLM) for already stored prompt responses using format-converter utilities.

## Architecture (proposed)
- MongoDB: Local dev via Docker image (reuse existing patterns from data-store examples).  
- Data layer: data-store module with Mongo backend.  
- Admin seeding: Conceptual trigger (could be a script or UI button) that inserts via data-store; no new FastAPI admin endpoints to build in this project.  
- Scraper: Use the existing data-retriever service and its `YahooFinanceRetriever` REST API. The mini-app UI will call the data-retriever API; no new scraper endpoints elsewhere. If external fetch is unavailable, use the retriever’s mock path to emit shaped data.  
- Prompt flow service: FastAPI endpoint that accepts a ticker, builds a prompt template via prompt-manager, validates/sanitizes via prompt-security, calls llm-provider **in mock mode for v1; architecture remains pluggable to swap in Bedrock/other providers later**, stores prompt+response in Mongo, and invokes format-converter to produce HTML/MD/JSON renderings.  
- UI: Minimal web pages (could be simple React or server-rendered) for:
  - Admin: trigger fake-company seeding; trigger scrape for tickers.
  - Prompt run: enter ticker → run prompt flow → display HTML render.  
  For now, scope is to define; implementation later.

## Data Shapes
- Seeded fake companies: mimic `data/input/sample_company_data.json` and `data/input/sample_stock_data.json` schemas (ticker, company, sector, metrics, etc.). 100 per invocation, randomly generated tickers/companies.
- Scraped entries: JSON shaped like the Yahoo metrics in `prompt/scrape_tickers.md` (valuation, financials, profitability fields). Stored in `seed_companies` collection with `source: "yahoo_finance"` and `ticker`.
- Prompt results: store `prompt`, `sanitized_prompt`, `llm_response_raw`, `llm_response_md`, `llm_response_html`, `metadata` (ticker, timestamp, model_used, run_id). Keep both MD and HTML variants for UI; HTML written by format-converter.

## Flows (with module calls and REST chains)
### A. Seed Data (Admin → data-store)
- REST chain: UI/trigger → POST data-store API `/bulk_store` (port 8007) with 100 generated company docs → data-store (Mongo) saves to `seed_companies` → response returns inserted keys/ids.

### B. Scrape Yahoo (Admin → data-retriever → data-store)
- REST chain: UI/trigger → POST data-retriever API `/retrieve` (port 8003) with `{"source":"yahoo_finance","query":{"tickers":[...]}}` → YahooFinanceRetriever (real or deterministic mock) → UI automatically persists to data-store `seed_companies` collection → UI displays last 10 results in table view (ticker + 4 fields).

### C. Prompt Flow (User UI → orchestrator → prompt-manager + prompt-security → llm-provider mock → data-store → format-converter)
- Parameters: ticker or company name (prefer array of tickers for future batch), selected from UI suggestions.  
- REST chain:  
  - UI autocompletes tickers/company names by calling data-store query (e.g., POST `/query` on port 8007) with filters on `ticker`/`company` using partial text; returns paginated suggestions.  
  - UI → POST miniapp orchestrator `/prompt/run` (local to stock-miniapp) with selected ticker(s).  
  - prompt-manager loads/fills template; prompt-security sanitizes.  
  - llm-provider **mock** generates response (v1).  
  - data-store stores (`prompt_runs`) via store API (e.g., POST `/store`).  
  - format-converter renders HTML/MD/JSON (persisted in Mongo and optionally filesystem).  
  - UI GET `/prompt/run/{id}` (or equivalent) to display HTML, link to MD/JSON.

### C.1 Browse & Filter Companies (UI → data-store → prompt flow shortcut)
- REST chain: UI → POST data-store `/query` with filters (e.g., marketCap > X, sort, pagination).  
- UI displays table with pagination/sorting; selecting a row auto-calls `/prompt/run` with that ticker (same flow as C).  

### D. Periodic Materialization (Optional → format-converter + data-store)
- Job → data-store query (`/query` or `/retrieve/{key}`) → format-converter regenerates MD/HTML/JSON (no LLM) → data-store store/bulk_store updated renders.

## Modules Reused (current state check)
- data-store: Mongo backend ready; examples include Mongo usage.  
- format-converter: can render HTML/MD/PDF; already used in full pipeline examples.  
- prompt-manager: FastAPI + Express proxy exist; templates and security middleware present.  
- prompt-security: available; optional dependency.  
- llm-provider: supports mock provider; use mock for this mini-app.  
- data-retriever: used for scraping. `YahooFinanceRetriever` exists; ensure its REST API returns the full `scrape_tickers.md` shape (real via yfinance/HTTP if allowed, otherwise deterministic mock). Browser mode stays optional.

## Endpoints (initial draft)
- (Conceptual) Seed trigger calls data-store insert; no new /admin API to be added here.  
- Scrape: call the existing data-retriever REST endpoint that wraps `YahooFinanceRetriever` with body {tickers: [...]}; returns summary.  
- `POST /prompt/run` → body: {ticker: “AAPL”}; runs prompt flow and returns {run_id, html_url?, md?, json?}.  
- `GET /prompt/run/{id}` → returns stored prompt/response (html/md/json metadata).  
- `GET /health` → service health.

## Assumptions & Constraints
- MongoDB via Docker; connection string `mongodb://localhost:27017`, DB `trainer_data`, collections: `seed_companies` (used for both seed data and scraped Yahoo Finance data), `prompt_runs`.  
- LLM calls default to mock provider (no external dependency).  
- Scraper is non-LLM and routed through `YahooFinanceRetriever`; implement the API path to output full metrics. If external fetch is out-of-scope, provide a deterministic mock matching `scrape_tickers.md`.  
- HTML rendering via format-converter, persisted to Mongo and optionally to filesystem for debugging.

## Risks / Open Points
- Prompt-security optional dependency: if not installed, must degrade gracefully.  
- Yahoo scraping may require user agent / throttling; retriever should handle rate limiting and offer a mock path if real fetch is disabled.  
- Grafana/Prometheus ports may conflict with Express (3000) if running together; plan port offsets if needed.

## Next Steps (after review)
1) Confirm data shapes and collections.  
2) Decide on real scrape vs simulated scraper for dev.  
3) Wire UI/admin triggers to existing data-retriever REST for scrape; seed trigger to data-store bulk insert.  
4) Add a minimal UI page to call `/prompt/run` and render HTML.  
5) Add a small CLI/cronable script for periodic format conversions.  

## Step-by-Step Implementation Proposal (for testing incrementally)

### Step 1: Verify MongoDB Docker instance and data-store connectivity ✅
**Status**: Completed  
- MongoDB container running on port 27017
- data-store module can connect and perform CRUD operations
- Collections ready: `seed_companies` (for both seed and scraped data), `prompt_runs`

---

### Step 2: Implement/confirm data-store bulk-insert utility for 100 fake companies

#### Overview
Create a **REST API endpoint** (FastAPI) for seeding companies and a **web UI** (Express + React) with an admin button to trigger the seeding. The UI calls the REST API, which stores data in MongoDB via data-store. This follows proper microservices architecture where the UI never directly accesses the database.

#### Architecture
```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   React UI      │  HTTP   │  Express Server  │  HTTP   │  FastAPI        │
│   (Browser)     │────────▶│  (Port 3000)     │────────▶│  (Port 8007)    │
│                 │         │  (Proxy/Static)   │         │  data-store API │
└─────────────────┘         └──────────────────┘         └─────────────────┘
                                                                      │
                                                                      ▼
                                                            ┌─────────────────┐
                                                            │   MongoDB       │
                                                            │   (Port 27017)  │
                                                            │   Collection:   │
                                                            │   seed_companies│
                                                            └─────────────────┘
```

**Key Design Principles:**
- ✅ UI (React) → Express Server → FastAPI → MongoDB (no direct DB access)
- ✅ REST API endpoint accepts collection parameter
- ✅ Can be triggered multiple times (adds more companies)
- ✅ Web UI provides admin interface with button

#### Implementation Details

##### 2.1 Data Generation Function (in data-store module)
**Location**: `_dev/data-store/src/data_store/utils/company_generator.py`

Generate fake companies matching the schema from `data/input/sample_company_data.json` and `data/input/sample_stock_data.json`.

**Key functions:**
- `generate_fake_company(ticker=None)` → Returns single company dict with key, data, metadata
- `generate_batch(count=100)` → Returns list of company dicts with unique tickers

**Data structure:**
```python
{
    "key": "company:AAPL",
    "data": {
        "company": {...},      # name, symbol, sector, industry, employees
        "financials": {...},    # revenue, net_income, assets, liabilities
        "stock_metrics": {...}  # ticker, price, volume, market_cap, pe_ratio, etc.
    },
    "metadata": {
        "source": "seed_data",
        "type": "company",
        "sector": "...",
        "industry": "..."
    }
}
```

##### 2.2 FastAPI REST Endpoint (in data-store API)
**Location**: `_dev/data-store/api_service.py` - Add new endpoint

**Endpoint**: `POST /admin/seed-companies`

**Request body:**
```json
{
  "count": 100,
  "collection": "seed_companies"
}
```

**Implementation approach:**
- Import `generate_batch` from `data_store.utils.company_generator`
- Create store instance with specified collection
- Generate companies, bulk store, return stats

**Response:**
```json
{
  "success": true,
  "records_loaded": 100,
  "total_in_collection": 100,
  "collection": "seed_companies",
  "errors": [],
  "keys": ["company:AAPL", ...]
}
```


#### Expected Flow
1. **User clicks "Seed Companies" button** in React UI
2. **React sends POST request** to Express server: `POST /api/admin/seed-companies`
3. **Express proxies request** to FastAPI: `POST http://localhost:8007/admin/seed-companies`
4. **FastAPI generates companies** using `data_store.utils.company_generator` (in data-store module)
5. **FastAPI stores in MongoDB** via data-store module (collection: `seed_companies`)
6. **FastAPI returns result** with count and status
7. **React displays success message** with statistics

#### Expected API Response
```json
{
  "success": true,
  "records_loaded": 100,
  "total_in_collection": 100,
  "collection": "seed_companies",
  "errors": [],
  "keys": ["company:AAPL", "company:MSFT", ...]
}
```

#### Verification
After seeding via UI:
```bash
# Via mongosh
docker exec mongodb mongosh trainer_data
db.seed_companies.countDocuments({})  # Should return 100 (or more if triggered multiple times)
db.seed_companies.findOne()  # View sample document

# Via data-store API
curl http://localhost:8007/query -X POST \
  -H "Content-Type: application/json" \
  -d '{"filters": {"metadata.source": "seed_data"}, "limit": 5}'

# Via UI: Click button again to add more companies (e.g., 50 more)
# Total will become 150
```

#### Files to Create
**Backend (data-store module):**
- `_dev/data-store/src/data_store/utils/company_generator.py` - Company generation logic
- `_dev/data-store/api_service.py` - **ADD** `/admin/seed-companies` endpoint

**Web Server (Express):**
- `_dev/stock-miniapp/web/server.js` - Express server with proxy
- `_dev/stock-miniapp/web/package.json` - Express dependencies

**Frontend (React):**
- `_dev/stock-miniapp/web/client/src/App.js` - Main React component
- `_dev/stock-miniapp/web/client/src/App.css` - Styles
- `_dev/stock-miniapp/web/client/package.json` - React dependencies

#### Running the Application

**1. Start FastAPI (data-store):**
```bash
cd _dev/data-store
python api_service.py
# Runs on http://localhost:8007
```

**2. Start Express Server:**
```bash
cd _dev/stock-miniapp/web
npm install
npm start
# Runs on http://localhost:3000
```

**3. Build React (for production):**
```bash
cd _dev/stock-miniapp/web/client
npm install
npm run build
# Builds to web/client/build/
```

**4. Access UI:**
- Open browser: `http://localhost:3000`
- Click "Seed Companies" button
- View results in UI

#### Key Benefits of This Architecture
- ✅ **Proper separation**: UI → API → Database (no direct DB access)
- ✅ **Reusable API**: FastAPI endpoint can be called from any client
- ✅ **Scalable**: Can add more admin features to the same UI
- ✅ **Testable**: Each layer can be tested independently
- ✅ **Multiple triggers**: Button can be clicked multiple times to add more companies

#### Dependencies
- `faker` (optional, for more realistic names) or simple random generation
- `requests` (for API-based script)
- `data-store` module (already available)

#### Testing
1. Run direct script: `python scripts/seed_companies_direct.py --count 100`
2. Verify in MongoDB: Check `seed_companies` collection
3. Test API script: Start data-store API, then run `python scripts/seed_companies.py --count 50`
4. Verify query: Use data-store API to query seeded companies

---

### Step 3: Implement YahooFinanceRetriever API-path to emit full `scrape_tickers.md` shape (real or deterministic mock); expose via existing data-retriever REST; test end-to-end write to data-store.

#### Overview
Complete the YahooFinanceRetriever implementation to return data matching the schema defined in `YAHOO_FINANCE_SCRAPING_INSTRUCTIONS.md` and `scrape_tickers.md`. The data-retriever REST API should retrieve the data and optionally store it in MongoDB via data-store. This is a **programmatic** operation (no LLM/prompt involved), reproducing the same data structure that would be obtained via browser automation.

#### Current State Analysis

**✅ What Exists:**
- `YahooFinanceRetriever` class in `_dev/data-retriever/src/data_retriever/retrievers/yahoo_finance_retriever.py`
- REST API endpoint: `POST /retrieve` on port 8003 (data-retriever service)
- Schema definition: `YAHOO_FINANCE_SCHEMA` matches the expected structure
- API accepts: `{"source": "yahoo_finance", "query": {"ticker": "AAPL"}}` or `{"tickers": ["AAPL", "MSFT"]}`

**❌ What's Missing:**
- `YahooFinanceRetriever._retrieve_via_api()` is a placeholder (returns empty structure)
- No integration with data-store for automatic persistence
- No deterministic mock implementation for development/testing

#### Expected Data Shape

The retrieved data must match the structure from `YAHOO_FINANCE_SCRAPING_INSTRUCTIONS.md`:

```json
{
  "ticker": "NVDA",
  "extractedAt": "2025-12-13T11:30:00.000Z",
  "valuation": {
    "marketCap": "4.42T",
    "enterpriseValue": "4.37T",
    "trailingPE": "51.67",
    "forwardPE": "26.95",
    "pegRatio": "0.78",
    "priceToSales": "27.06",
    "priceToBook": "44.10",
    "enterpriseValueRevenue": "26.46",
    "enterpriseValueEBITDA": "42.37"
  },
  "financials": {
    "revenue": "165.22B",
    "revenuePerShare": "6.76",
    "quarterlyRevenueGrowth": "55.60%",
    "grossProfit": "115.4B",
    "ebitda": "98.28B",
    "netIncome": "86.6B",
    "earningsPerShare": "3.52",
    "quarterlyEarningsGrowth": "59.20%"
  },
  "profitability": {
    "profitMargin": "52.41%",
    "operatingMargin": "60.84%",
    "returnOnAssets": "53.09%",
    "returnOnEquity": "109.42%"
  }
}
```

#### Implementation Requirements

##### 3.1 Complete YahooFinanceRetriever._retrieve_via_api() Implementation

**Location**: `_dev/data-retriever/src/data_retriever/retrievers/yahoo_finance_retriever.py`

**Primary Solution: yfinance Library**

**Why yfinance over web scraping:**
- ✅ **Simpler**: No browser automation (Selenium/Playwright) needed
- ✅ **Faster**: Direct API calls, no page rendering overhead
- ✅ **More reliable**: Less brittle than HTML scraping
- ✅ **Structured data**: Returns Python dicts/DataFrames directly
- ✅ **Lower maintenance**: No selectors to update when Yahoo changes HTML
- ✅ **Built-in rate limiting**: Handles throttling automatically
- ✅ **Free & no registration**: Open-source (Apache 2.0), no API keys needed
- ✅ **Industry standard**: Widely used and actively maintained

**Dependency Management:**

Add `yfinance` to `pyproject.toml` as an optional dependency:

```toml
[project.optional-dependencies]
yahoo = [
    "yfinance>=0.2.0",
]
all = [
    # ... other dependencies
    "yfinance>=0.2.0",
]
```

**Installation:**
```bash
# Install module with yahoo support
pip install -e ".[yahoo]"

# Or install with all optional dependencies
pip install -e ".[all]"
```

**For AWS Deployment:**
- Dependencies are explicitly declared in `pyproject.toml`
- No manual `pip install` commands needed
- Use `pip install -e ".[yahoo]"` or `pip install -e ".[all]"` in deployment scripts
- Version pinning ensures consistent deployments

**Implementation Strategy:**

1. **Primary: yfinance (real data)** - Default behavior
2. **Fallback: Deterministic mock** - For testing/offline/rate limit scenarios
3. **Future: Browser scraping** - Last resort if yfinance fails

**Configuration Management: useMock**

**Per-Module .env Files (Recommended):**
Each module has its own `.env` file for self-contained configuration:
- `_dev/data-retriever/.env` - Module-specific config (gitignored)
- `_dev/data-retriever/.env.example` - Template (committed to git)

**Configuration Levels (Priority Order):**
1. **Query Parameter** (per-request override) - Highest priority
2. **Constructor Parameter** (per-instance) - Set in `api_service.py`
3. **Environment Variable** (from `.env` or AWS) - Global default
4. **Hard-coded Default** (`False` = use real yfinance) - Fallback

**Local Development:**
- `.env` file in module directory (`_dev/data-retriever/.env`)
- `python-dotenv` loads it automatically in `api_service.py`
- Variables available via `os.getenv()`

**AWS Deployment:**
- Set environment variables in Lambda/ECS/EC2
- Same variable names as `.env` file
- No `.env` file needed (env vars already set)
- Code works identically (reads from `os.getenv()`)

**Benefits:**
- ✅ Self-contained modules (each module has its own config)
- ✅ Variables defined where used (in module directory)
- ✅ Easy module distribution (include `.env.example` in package)
- ✅ Mini-apps use only needed modules (set only relevant env vars)
- ✅ Clear separation (no cross-module config dependencies)

**Implementation approach:**
```python
# In api_service.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from module directory
module_dir = Path(__file__).parent
env_file = module_dir / ".env"
load_dotenv(env_file)

# Read from environment (with default)
default_use_mock = os.getenv("YAHOO_FINANCE_USE_MOCK", "false").lower() == "true"

# Initialize retriever with config
retrievers["yahoo_finance"] = YahooFinanceRetriever(
    cache=cache,
    enable_metrics=True,
    use_mock=default_use_mock  # From .env or environment
)

# In YahooFinanceRetriever.__init__()
def __init__(self, use_mock: bool = False, **kwargs):
    """
    Initialize Yahoo Finance retriever.
    
    Args:
        use_mock: Whether to use mock data (default: False, uses real yfinance)
        **kwargs: Additional arguments passed to DataRetriever
    """
    super().__init__(source_name="yahoo_finance", **kwargs)
    self.use_mock = use_mock  # Store instance variable
    # ... rest of initialization

# In _retrieve_via_api()
def _retrieve_via_api(self, ticker: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Retrieve data via yfinance API with mock fallback.
    
    Priority: query param > instance variable > env var > False
    """
    # Check query parameter first (highest priority)
    use_mock = query.get("use_mock", self.use_mock)  # Falls back to instance variable
    
    if use_mock:
        return self._generate_mock_data(ticker)
    
    try:
        return self._fetch_real_data(ticker)  # Use yfinance
    except Exception as e:
        # Fallback to mock if yfinance fails (rate limit, network error, etc.)
        logger.warning(f"yfinance failed for {ticker}: {e}, using mock")
        return self._generate_mock_data(ticker)

def _fetch_real_data(self, ticker: str) -> Optional[Dict[str, Any]]:
    """
    Fetch real data using yfinance library.
    
    Maps yfinance data structure to expected Yahoo Finance schema.
    """
    try:
        import yfinance as yf
    except ImportError:
        raise ImportError("yfinance not installed. Install with: pip install -e '.[yahoo]'")
    
    stock = yf.Ticker(ticker)
    info = stock.info
    
    # Map yfinance data to expected schema format
    # Extract and format all required fields from info dict
    # Convert numbers to strings with proper suffixes (T, B, M, %)
    # Return structured data matching YAHOO_FINANCE_SCHEMA
```

**yfinance Data Mapping:**

The `stock.info` dictionary contains most required fields:
- `marketCap` → `valuation.marketCap` (convert to string with suffix)
- `enterpriseValue` → `valuation.enterpriseValue`
- `trailingPE` → `valuation.trailingPE`
- `forwardPE` → `valuation.forwardPE`
- `pegRatio` → `valuation.pegRatio`
- `priceToSalesTrailing12Months` → `valuation.priceToSales`
- `priceToBook` → `valuation.priceToBook`
- `totalRevenue` → `financials.revenue`
- `ebitda` → `financials.ebitda`
- `netIncomeToCommon` → `financials.netIncome`
- `profitMargins` → `profitability.profitMargin`
- `operatingMargins` → `profitability.operatingMargin`
- `returnOnAssets` → `profitability.returnOnAssets`
- `returnOnEquity` → `profitability.returnOnEquity`
- And more...

**Note on yfinance:**
- Free and open-source (Apache 2.0 license)
- No registration or API keys required
- Uses Yahoo Finance's public endpoints (not an official API)
- Subject to Yahoo's rate limits (yfinance handles retries automatically)
- May break if Yahoo changes their endpoints (yfinance is actively maintained)

##### 3.2 Automatic Persistence to seed_companies Collection

**Location**: `_dev/stock-miniapp/web/client/src/App.js` - Add scrape section and table view

**Key Requirements:**
1. **Automatic Persistence**: When retrieving via yfinance, automatically persist to `seed_companies` collection (same as Step 2)
2. **Batch Support**: Support retrieving multiple tickers at once
3. **Unified Table View**: Display ticker + 4 meaningful fields in a table
4. **Last 10 Results**: Show the last 10 retrieved items (or less if fewer tickers submitted)
5. **Reusable View**: Same table view for both seed companies (Step 2) and scraped data (Step 3)

**Flow:**
1. UI calls data-retriever API: `POST /retrieve` with multiple tickers
2. Data-retriever returns Yahoo Finance data
3. UI automatically calls data-store API: `POST /bulk_store` to persist to `seed_companies` collection
4. UI displays results in a table with ticker + 4 fields

**Table Columns (4 Meaningful Fields):**
- **Ticker** (always shown)
- **Market Cap** (`valuation.marketCap`)
- **Revenue** (`financials.revenue`)
- **Profit Margin** (`profitability.profitMargin`)
- **P/E Ratio** (`valuation.trailingPE`)

**Data Transformation for Storage:**
```json
{
  "key": "company:AAPL:2025-12-13T11:30:00",
  "data": {
    "ticker": "AAPL",
    "extractedAt": "2025-12-13T11:30:00.000Z",
    "valuation": { /* ... */ },
    "financials": { /* ... */ },
    "profitability": { /* ... */ }
  },
  "metadata": {
    "source": "yahoo_finance",
    "ticker": "AAPL",
    "extracted_at": "2025-12-13T11:30:00.000Z"
  }
}
```

**UI Implementation:**
- Add new section for "Scrape Yahoo Finance Data"
- Input field for tickers (comma-separated or array)
- Button to trigger retrieval
- Table component showing last 10 results with 5 columns (ticker + 4 fields)
- Reuse same table component for seed companies view

##### 3.3 REST API Call Chain

**Flow B (Updated for automatic persistence to seed_companies):**
```
UI/Admin → POST data-retriever /retrieve (port 8003)
  → YahooFinanceRetriever retrieves data (batch: ["AAPL", "MSFT", ...])
  → Returns data to UI
UI/Admin → POST data-store /bulk_store (port 8007)  
  → Automatically stores scraped data in MongoDB collection "seed_companies"
  → Same collection as Step 2 (unified storage)
UI/Admin → GET data-store /query (port 8007)
  → Retrieves last 10 items from "seed_companies" collection
  → Displays in table view (ticker + 4 fields: Market Cap, Revenue, Profit Margin, P/E Ratio)
```

**Example API Calls:**

**Step 1: Retrieve from Yahoo Finance**
```bash
# Real data (default - requires yfinance installed)
curl -X POST http://localhost:8003/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "source": "yahoo_finance",
    "query": {
      "tickers": ["AAPL", "MSFT"]
    }
  }'

# Mock data (for testing/offline)
curl -X POST http://localhost:8003/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "source": "yahoo_finance",
    "query": {
      "tickers": ["AAPL", "MSFT"],
      "use_mock": true
    }
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "tickers": [
      {
        "ticker": "AAPL",
        "extractedAt": "2025-12-13T11:30:00.000Z",
        "valuation": { /* ... */ },
        "financials": { /* ... */ },
        "profitability": { /* ... */ }
      },
      {
        "ticker": "MSFT",
        "extractedAt": "2025-12-13T11:30:00.000Z",
        "valuation": { /* ... */ },
        "financials": { /* ... */ },
        "profitability": { /* ... */ }
      }
    ]
  },
  "source": "yahoo_finance",
  "metadata": {
    "retrieved_at": "2025-12-13T11:30:00.000Z",
    "ticker_count": 2
  }
}
```

**Step 2: Store in data-store**
```bash
curl -X POST http://localhost:8007/bulk_store \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "key": "scrape:AAPL:2025-12-13T11:30:00",
        "data": { /* full yahoo finance data */ },
        "metadata": {
          "source": "yahoo_finance",
          "ticker": "AAPL",
          "extracted_at": "2025-12-13T11:30:00.000Z"
        }
      },
      {
        "key": "scrape:MSFT:2025-12-13T11:30:00",
        "data": { /* full yahoo finance data */ },
        "metadata": {
          "source": "yahoo_finance",
          "ticker": "MSFT",
          "extracted_at": "2025-12-13T11:30:00.000Z"
        }
      }
    ],
    "collection": "seed_companies"
  }'
```

#### Verification via Docker/MongoDB

After scraping and storing, verify data in MongoDB:

**Via mongosh (Docker):**
```bash
# Connect to MongoDB
docker exec -it mongodb mongosh trainer_data

# Count all companies (seed + scraped)
db.seed_companies.countDocuments({})

# View one example
db.seed_companies.findOne({"data.ticker": "AAPL"})

# Query by ticker
db.seed_companies.find({"data.ticker": "AAPL"}).pretty()

# Query by source (seed vs yahoo_finance)
db.seed_companies.find({"metadata.source": "yahoo_finance"}).pretty()

# Get last 10 items (for table display)
db.seed_companies.find().sort({"stored_at": -1}).limit(10).pretty()

# Count by source
db.seed_companies.aggregate([
  {"$group": {"_id": "$metadata.source", "count": {"$sum": 1}}}
])
```

**Via Python script:**
```python
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['trainer_data']
collection = db['seed_companies']

# Count
count = collection.count_documents({})
print(f"Total scraped metrics: {count}")

# Get one example
example = collection.find_one({"metadata.ticker": "AAPL"})
print(example)
```

#### Files to Modify/Create

**Backend (data-retriever module):**
- `_dev/data-retriever/pyproject.toml`
  - Add `yfinance>=0.2.0` to `[project.optional-dependencies]` under `yahoo` and `all`
  - Add `python-dotenv>=1.0.0` to `dependencies` (for .env file support)
  
- `_dev/data-retriever/api_service.py`
  - Add `python-dotenv` import and load `.env` from module directory
  - Read `YAHOO_FINANCE_USE_MOCK` from environment
  - Pass `use_mock` parameter to `YahooFinanceRetriever` constructor
  
- `_dev/data-retriever/src/data_retriever/retrievers/yahoo_finance_retriever.py`
  - Add `use_mock` parameter to `__init__()` method
  - Store as instance variable `self.use_mock`
  - Implement `_retrieve_via_api()` with priority: query param > instance > env > default
  - Implement `_fetch_real_data(ticker)` using yfinance library
  - Map yfinance `stock.info` data to expected schema format
  - Implement `_generate_mock_data(ticker)` for fallback/testing
  - Ensure all required fields from schema are populated
  - Handle ImportError if yfinance not installed (graceful degradation)

**Configuration Files:**
- `_dev/data-retriever/.env` (gitignored)
  - Module-specific configuration
  - Create from `.env.example` template
  - Contains: `YAHOO_FINANCE_USE_MOCK=false`
  
- `_dev/data-retriever/.env.example` (committed to git)
  - Template for `.env` file
  - Documents all available configuration options
  - Example content:
    ```bash
    # Yahoo Finance Retriever Configuration
    # Set to true for offline testing, false for real data
    YAHOO_FINANCE_USE_MOCK=false
    
    # Data Retriever Service Configuration
    DATA_RETRIEVER_PORT=8003
    ENABLE_CACHE=true
    ```

#### Testing Plan

1. **Unit Test**: Test `YahooFinanceRetriever._retrieve_via_api()` returns correct schema
2. **API Test**: Test `POST /retrieve` endpoint with yahoo_finance source
3. **Integration Test**: 
   - Call data-retriever API
   - Transform response to data-store format
   - Call data-store API to store
   - Verify in MongoDB via docker commands
4. **Schema Validation**: Ensure returned data matches `YAHOO_FINANCE_SCHEMA`

#### Success Criteria

- ✅ `yfinance>=0.2.0` added to `pyproject.toml` optional dependencies
- ✅ `YahooFinanceRetriever._retrieve_via_api()` uses yfinance as primary solution
- ✅ `_fetch_real_data()` implemented to map yfinance data to schema
- ✅ `_generate_mock_data()` implemented as fallback
- ✅ Returns data matching the full schema from `YAHOO_FINANCE_SCRAPING_INSTRUCTIONS.md`
- ✅ All fields from schema are present and properly formatted (strings with suffixes)
- ✅ Data can be retrieved via REST API: `POST /retrieve` with `source: "yahoo_finance"`
- ✅ Data can be stored in MongoDB via data-store API
- ✅ Data verified in MongoDB collection `seed_companies` via docker/mongosh
- ✅ Supports both single ticker and batch tickers
- ✅ Graceful fallback to mock if yfinance fails or not installed
- ✅ Mock data is deterministic (same ticker = same data)
- ✅ Dependencies properly managed for AWS deployment

#### Dependencies

**Required:**
- `data-store` module (for MongoDB persistence)
- MongoDB Docker container (already running)
- `python-dotenv>=1.0.0` - For `.env` file support (declared in `pyproject.toml` dependencies)

**Optional (declared in pyproject.toml):**
- `yfinance>=0.2.0` - For real Yahoo Finance data retrieval
  - Install: `pip install -e ".[yahoo]"` or `pip install -e ".[all]"`
  - Free, no registration required
  - Primary solution for data retrieval

**For AWS Deployment:**
- All dependencies are declared in `pyproject.toml`
- Use `pip install -e ".[yahoo]"` or `pip install -e ".[all]"` in deployment
- No manual pip installs needed - everything is version-controlled

#### Notes

- **Programmatic**: No LLM/prompt involved - pure data retrieval
- **Primary Solution**: yfinance library (real data, free, no registration)
- **Fallback**: Deterministic mock for testing/offline scenarios
- **Schema Compliance**: Must match `YAHOO_FINANCE_SCRAPING_INSTRUCTIONS.md` exactly
- **Separation of Concerns**: data-retriever retrieves, data-store persists (two-step flow)
- **Dependency Management**: All dependencies declared in `pyproject.toml` for clean AWS deployment
- **Rate Limiting**: yfinance handles Yahoo's rate limits automatically with retries
- **Configuration**: Per-module `.env` files for self-contained modules
  - Local: `.env` file in module directory (gitignored)
  - AWS: Environment variables with same names (no `.env` file needed)
  - Priority: Query param > Constructor > Environment > Default
  - Benefits: Self-contained modules, easy distribution, mini-app flexibility  
### Step 4: Build minimal UI/endpoint to trigger scrape via data-retriever and show summary from data-store.

**Note**: Step 4 is now integrated into Step 3:
- UI automatically persists scraped data to `seed_companies` collection
- Table view displays ticker + 4 meaningful fields (Market Cap, Revenue, Profit Margin, P/E Ratio)
- Shows last 10 results (or less if fewer tickers)
- Same table view used for both seed companies and scraped data  
### Step 5: Prompt flow v1 (mock LLM): prompt-manager + prompt-security + llm-provider mock; persist to data-store; render via format-converter; minimal UI page to run and view HTML.  
### Step 6: Optional periodic job: regenerate MD/HTML/JSON from stored prompt responses (format-converter) and persist.  
### Step 7: Hardening & metrics: ensure Prometheus metrics exposed from involved services; basic dashboards optional.  
### Step 8: Later (not in first iteration): swap llm-provider mock to Bedrock by configuration only; no flow changes.  

Please review and adjust before we implement.

