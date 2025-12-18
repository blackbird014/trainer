# Stock Mini App - Specification Draft (Review Before Implementation)

## Goal
Draft a usage demo (mini‑app spec) that reuses existing modules (data-store, data-retriever, prompt-manager, prompt-security, llm-provider, format-converter) with the already-defined MongoDB Docker instance. This is a specification only; no new mini-app code or new services/endpoints are to be implemented here.

## High-Level Capabilities
1) Seed test data into MongoDB (100 fake companies per request). Trigger should call an existing data-store API/utility that supports insert/bulk-insert (or a small data-store endpoint for this purpose if already provided); if not present, we’ll add this call to data-store rather than creating a separate app-specific service.  
2) Web admin action to scrape Yahoo Finance for given tickers (no LLM), routed through the existing data-retriever service and its `YahooFinanceRetriever` REST API. Store results in MongoDB via data-store.  
3) Web UI flow to run a prompt-driven analysis for a ticker (uses prompt-manager + prompt-security + llm-provider **mock only for first iteration; design stays pluggable to later point to Bedrock or other backends**). Persist prompt + response to MongoDB; render HTML via format-converter; keep MD/JSON variants.  
4) Optional periodic job to materialize MD/HTML/JSON versions (no LLM) for already stored prompt responses using format-converter utilities.

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        STOCK MINI-APP                                │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Frontend (React + Express)                                   │ │
│  │  - Admin Panel: Seed Companies, Scrape Tickers                │ │
│  │  - Company Table: Display last 10, "Analyze" button per row   │ │
│  │  - Prompt Results: Display HTML/MD/JSON output                │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                              │                                       │
│                              │ REST API                              │
│                              ▼                                       │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Orchestrator Service (FastAPI)                               │ │
│  │  - Coordinates microservice calls                             │ │
│  │  - Manages workflow state                                     │ │
│  │  - Handles errors and retries                                 │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                              │                                       │
│        ┌────────────────────┼────────────────────┐                  │
│        │                      │                    │                  │
│        ▼                      ▼                    ▼                  │
│  ┌──────────┐         ┌──────────┐         ┌──────────┐          │
│  │ data-    │         │ prompt-  │         │ llm-     │          │
│  │ retriever│         │ manager  │         │ provider  │          │
│  │ :8003    │         │ :8000    │         │ :8001     │          │
│  └──────────┘         └──────────┘         └──────────┘          │
│        │                      │                    │                  │
│        │                      ▼                    │                  │
│        │              ┌──────────┐                 │                  │
│        │              │ prompt-  │                 │                  │
│        │              │ security │                 │                  │
│        │              │ :8002    │                 │                  │
│        │              └──────────┘                 │                  │
│        │                      │                    │                  │
│        └──────────────────────┼────────────────────┘                  │
│                               │                                      │
│                               ▼                                      │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  data-store (FastAPI)                                        │ │
│  │  - MongoDB backend                                            │ │
│  │  - Collections: seed_companies, prompt_runs                   │ │
│  │  :8007                                                        │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                               │                                      │
│                               ▼                                      │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  format-converter (FastAPI)                                   │ │
│  │  - MD → HTML/JSON conversion                                  │ │
│  │  :8004                                                        │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   MongoDB        │
                    │   (Docker)       │
                    │   :27017         │
                    │                  │
                    │ Collections:     │
                    │ - seed_companies │
                    │ - prompt_runs    │
                    └──────────────────┘
```

### Microservices Architecture

Each module runs as an independent FastAPI service:

- **data-retriever** (Port 8003): Retrieves data from Yahoo Finance
- **data-store** (Port 8007): Persists data to MongoDB
- **prompt-manager** (Port 8000): Manages prompt templates and context
- **prompt-security** (Port 8002): Validates and sanitizes prompts (optional)
- **llm-provider** (Port 8001): Generates LLM responses (mock or real)
- **format-converter** (Port 8004): Converts between formats (MD/HTML/JSON)
- **stock-miniapp orchestrator** (Port 3001/api): Coordinates workflow

### Data Flow

**Flow A: Seed Companies**
```
UI → data-store /bulk_store → MongoDB (seed_companies)
```

**Flow B: Scrape Yahoo Finance**
```
UI → data-retriever /retrieve → yfinance API
UI → data-store /bulk_store → MongoDB (seed_companies)
UI → data-store /query → Display in table
```

**Flow C: Prompt Flow (Orchestrated)**
```
UI → orchestrator /prompt/run
  → data-store (get company data)
  → prompt-manager (load contexts, fill template)
  → prompt-security (validate)
  → llm-provider (generate response)
  → data-store (store prompt + response)
  → format-converter (render HTML/MD/JSON)
  → data-store (update with formats)
  → UI (display result)
```

## Architecture (Detailed)
- MongoDB: Local dev via Docker image (reuse existing patterns from data-store examples).  
- Data layer: data-store module with Mongo backend.  
- Admin seeding: Conceptual trigger (could be a script or UI button) that inserts via data-store; no new FastAPI admin endpoints to build in this project.  
- Scraper: Use the existing data-retriever service and its `YahooFinanceRetriever` REST API. The mini-app UI will call the data-retriever API; no new scraper endpoints elsewhere. If external fetch is unavailable, use the retriever's mock path to emit shaped data.  
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
### Step 5: Prompt Flow v1 (Mock LLM) - Orchestrator Pattern

#### Overview
Implement the prompt-driven analysis flow for tickers, starting from the existing admin panel. Users can trigger prompt analysis directly from the company table by clicking a button on each row. This step introduces the **orchestrator pattern** to coordinate multiple microservices (prompt-manager, prompt-security, llm-provider, data-store, format-converter) into a cohesive workflow.

#### Current State
- ✅ Admin panel exists with company table showing last 10 companies
- ✅ Table displays: Ticker, Retrieved, Market Cap, Revenue, Profit Margin, P/E Ratio
- ✅ Companies are stored in MongoDB `seed_companies` collection
- ✅ UI can query and display companies from data-store

#### Updated Flow C (Starting from Admin Panel)

**Initial Implementation (v1):**
- **Entry Point**: Admin panel "Last 10 Companies" table
- **Trigger**: "Analyze" button on each row
- **Postponed**: UI autocomplete/search (will be added in future iteration)

**REST API Call Chain:**
```
UI (Admin Panel) 
  → Click "Analyze" button on row (ticker: "AAPL")
  → POST stock-miniapp orchestrator /prompt/run (port 3001)
    → Orchestrator coordinates:
      1. GET data-store /retrieve/{key} (port 8007) - Fetch company data
      2. POST prompt-manager /prompt/load-contexts (port 8000) - Load context files
      3. POST prompt-manager /prompt/fill (port 8000) - Fill template with ticker + company data
      4. POST prompt-security /validate (if available) - Sanitize prompt
      5. POST llm-provider /generate (port 8001) - Generate response (MOCK mode)
      6. POST data-store /store (port 8007) - Store prompt + response in `prompt_runs` collection
      7. POST format-converter /convert (port 8004) - Render HTML/MD/JSON
      8. POST data-store /update/{key} (port 8007) - Update prompt_runs with rendered formats
    → Return: {run_id, ticker, html_url, status}
  → UI displays HTML result in modal/new page
```

#### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         STOCK MINI-APP UI                               │
│                    (React - Port 3001)                                  │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │  Admin Panel - "Last 10 Companies" Table                       │   │
│  │  ┌──────────┬──────────┬──────────┬──────────┬──────────┐     │   │
│  │  │ Ticker   │ Market   │ Revenue  │ Profit   │ P/E      │     │   │
│  │  │          │ Cap      │          │ Margin   │ Ratio    │     │   │
│  │  ├──────────┼──────────┼──────────┼──────────┼──────────┤     │   │
│  │  │ AAPL     │ 4.13T    │ 416.16B  │ 25.31%   │ 28.45    │ [A] │   │
│  │  │ MSFT     │ 3.56T    │ 293.81B  │ 35.12%   │ 32.10    │ [A] │   │
│  │  │ NVDA     │ 4.26T    │ 187.14B  │ 53.01%   │ 43.32    │ [A] │   │
│  │  └──────────┴──────────┴──────────┴──────────┴──────────┘     │   │
│  │                    [A] = "Analyze" Button                        │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │  Prompt Result Display (Modal/New Page)                        │   │
│  │  - HTML rendered output                                        │   │
│  │  - Links to MD/JSON versions                                  │   │
│  │  - Metadata (ticker, timestamp, model used)                   │   │
│  └────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ POST /prompt/run
                                    │ {ticker: "AAPL"}
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    STOCK-MINIAPP ORCHESTRATOR                            │
│              (FastAPI Service - Port 3001/api)                          │
│                                                                          │
│  Orchestrator Responsibilities:                                          │
│  1. Coordinate multiple microservice calls                              │
│  2. Handle errors and retries                                           │
│  3. Transform data between services                                     │
│  4. Manage workflow state                                                │
│  5. Return unified response to UI                                      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
        ┌─────────────────┐ ┌──────────────┐ ┌──────────────┐
        │  data-store     │ │ prompt-      │ │ llm-provider │
        │  (Port 8007)    │ │ manager      │ │ (Port 8001)  │
        │                 │ │ (Port 8000)   │ │              │
        │ GET /retrieve   │ │ POST /prompt │ │ POST /generate│
        │ POST /store     │ │ /load-context│ │ (MOCK mode)  │
        │ POST /update    │ │ POST /prompt │ │              │
        └─────────────────┘ │ /fill        │ └──────────────┘
                             └──────────────┘
                    │               │
                    ▼               ▼
        ┌─────────────────┐ ┌──────────────┐
        │ format-converter│ │ prompt-      │
        │ (Port 8004)     │ │ security     │
        │                 │ │ (Optional)   │
        │ POST /convert   │ │ POST /validate│
        │ (MD→HTML/JSON)  │ │              │
        └─────────────────┘ └──────────────┘
                                    │
                                    ▼
                        ┌──────────────────────┐
                        │   MongoDB            │
                        │   (Port 27017)       │
                        │                      │
                        │ Collections:         │
                        │ - seed_companies     │
                        │ - prompt_runs        │
                        └──────────────────────┘
```

#### Orchestrator Concept

**Important: Orchestrator is App-Dependent, Not a Module**

The orchestrator is **application-specific workflow logic**, not a reusable module. It lives in `_dev/stock-miniapp/api/` and is specific to the stock-miniapp's needs. Other mini-apps can:
- Create their own orchestrators for their specific workflows
- Call modules directly (bypassing orchestrator)
- Reuse modules independently

**Why App-Dependent?**
- Modules are reusable across applications
- Orchestrator encodes this app's specific workflow
- Different apps need different orchestration patterns
- Keeps modules independent and reusable

**Implementation Scope:**
- **Flow C (Prompt Flow)**: Uses orchestrator (complex, 5-8 service calls)
- **Flow A (Seed)**: Direct call (simple, single service)
- **Flow B (Scrape)**: Direct calls (simple, two services)

**What is an Orchestrator?**
An orchestrator is a service that coordinates multiple microservices to complete a complex workflow. Instead of having the UI call each service directly, the orchestrator:
1. **Orchestrates the flow**: Determines the sequence of service calls
2. **Manages state**: Tracks progress through the workflow
3. **Handles errors**: Provides retry logic and error recovery
4. **Transforms data**: Converts data formats between services
5. **Provides unified API**: Single endpoint for complex operations

**Why Use an Orchestrator?**
- ✅ **Simplifies UI**: UI makes one call instead of 5-8 calls
- ✅ **Centralized logic**: Business workflow logic in one place
- ✅ **Error handling**: Centralized retry and error recovery
- ✅ **Transaction-like behavior**: Can rollback or compensate on failure
- ✅ **Monitoring**: Single point to track workflow metrics
- ✅ **Future extensibility**: Easy to add steps (e.g., caching, validation)

**Orchestrator vs Direct Calls:**
```
❌ Without Orchestrator (Complex UI):
UI → data-store (get company)
UI → prompt-manager (load contexts)
UI → prompt-manager (fill template)
UI → prompt-security (validate)
UI → llm-provider (generate)
UI → data-store (store response)
UI → format-converter (render)
UI → data-store (update with HTML)

✅ With Orchestrator (Simple UI):
UI → orchestrator /prompt/run (one call)
Orchestrator → coordinates all services internally
UI ← orchestrator (unified response)
```

**Orchestrator Implementation Pattern:**
```python
# _dev/stock-miniapp/api/orchestrator.py
class PromptOrchestrator:
    def __init__(self):
        self.data_store_url = "http://localhost:8007"
        self.prompt_manager_url = "http://localhost:8000"
        self.llm_provider_url = "http://localhost:8001"  # REST API service
        self.format_converter_url = "http://localhost:8004"
        self.prompt_security_url = "http://localhost:8002"  # Optional
    
    async def run_prompt_flow(self, ticker: str) -> Dict[str, Any]:
        """
        Orchestrate the complete prompt flow for a ticker.
        
        Steps:
        1. Fetch company data from data-store
        2. Load context files via prompt-manager
        3. Fill prompt template with ticker + company data
        4. Validate/sanitize prompt (if security module available)
        5. Generate LLM response (mock mode)
        6. Store prompt + response in data-store
        7. Convert response to HTML/MD/JSON via format-converter
        8. Update stored response with rendered formats
        9. Return unified response to UI
        """
        run_id = str(uuid.uuid4())
        
        try:
            # Step 1: Fetch company data
            # Calls data-store API to retrieve company financial data from MongoDB seed_companies collection.
            # Returns company data structure with valuation, financials, profitability fields.
            company_data = await self._fetch_company_data(ticker)
            
            # Step 2: Load context files
            # Calls prompt-manager API to load markdown context files from disk (e.g., biotech/01-introduction.md).
            # Merges multiple context files into a single string for prompt composition.
            contexts = await self._load_contexts()
            
            # Step 3: Fill prompt template
            # Calls prompt-manager API to fill template variables with ticker, company_data, and contexts.
            # Returns a complete prompt string ready for LLM processing.
            filled_prompt = await self._fill_prompt(ticker, company_data, contexts)
            
            # Step 4: Validate prompt (optional)
            # Calls prompt-security API to validate and sanitize the filled prompt for injection attacks.
            # Returns sanitized prompt string, or original if security module unavailable (graceful degradation).
            sanitized_prompt = await self._validate_prompt(filled_prompt)
            
            # Step 5: Generate LLM response
            # Calls llm-provider REST API (port 8001) to generate response from sanitized prompt.
            # Supports provider swapping via request parameters (use_mock=true for v1).
            # Returns response with content, tokens_used, model, cost, and metadata.
            llm_response = await self._generate_response(sanitized_prompt, ticker)
            
            # Step 6: Store in data-store
            # Calls data-store API to persist prompt run in MongoDB prompt_runs collection.
            # Stores run_id, ticker, prompt, raw LLM response, and metadata; returns stored key.
            stored_key = await self._store_prompt_run(run_id, ticker, sanitized_prompt, llm_response)
            
            # Step 7: Convert to HTML/MD/JSON
            # Calls format-converter API to render LLM response (markdown) into HTML, MD, and JSON formats.
            # Returns dictionary with html, md, and json keys containing rendered content.
            rendered_formats = await self._render_formats(llm_response)
            
            # Step 8: Update with rendered formats
            # Calls data-store API to update the stored prompt run with HTML/MD/JSON rendered formats.
            # Updates the prompt_runs document with llm_response_html, llm_response_md, llm_response_json fields.
            await self._update_with_formats(stored_key, rendered_formats)
            
            return {
                "success": True,
                "run_id": run_id,
                "ticker": ticker,
                "html_url": f"/prompt/run/{run_id}/html",
                "md_url": f"/prompt/run/{run_id}/md",
                "json_url": f"/prompt/run/{run_id}/json",
                "status": "completed"
            }
        except Exception as e:
            # Error handling and logging
            return {
                "success": False,
                "run_id": run_id,
                "error": str(e),
                "status": "failed"
            }
```

#### Implementation Details

##### 5.1 Add "Analyze" Button to Company Table

**Location**: `_dev/stock-miniapp/web/client/src/App.js`

**Changes:**
- Add "Analyze" button column to `CompanyTable` component
- Button triggers `handleAnalyzePrompt(ticker)` function
- Show loading state while orchestrator processes request (10-20 seconds expected)
- **UI Behavior (v1)**: Opens modal immediately, shows loading spinner, waits synchronously for orchestrator response
- Display result in modal when complete (HTML/MD/JSON tabs)
- **Note**: For v1, modal waits synchronously. Future enhancement: async/polling pattern for better UX

**UI Flow:**
```javascript
// In CompanyTable component
<tbody>
  {companies.map((company, idx) => (
    <tr key={idx}>
      <td>{data.ticker}</td>
      <td>{formatDate(retrievalDate)}</td>
      <td>{valuation.marketCap}</td>
      <td>{financials.revenue}</td>
      <td>{profitability.profitMargin}</td>
      <td>{valuation.trailingPE}</td>
      <td>
        <button 
          onClick={() => handleAnalyzePrompt(data.ticker)}
          disabled={analyzing === data.ticker}
        >
          {analyzing === data.ticker ? 'Analyzing...' : 'Analyze'}
        </button>
      </td>
    </tr>
  ))}
</tbody>
```

##### 5.2 Create Orchestrator Service

**Location**: `_dev/stock-miniapp/api/orchestrator.py` (new file)

**Responsibilities:**
- Coordinate all microservice calls
- Handle errors and retries
- Transform data between services
- Return unified response

**FastAPI Endpoint:**
```python
# _dev/stock-miniapp/api/orchestrator_service.py
from fastapi import FastAPI, HTTPException
from orchestrator import PromptOrchestrator

app = FastAPI()
orchestrator = PromptOrchestrator()

@app.post("/prompt/run")
async def run_prompt_flow(request: PromptRunRequest):
    """
    Orchestrate prompt flow for a ticker.
    
    Request: {ticker: "AAPL"}
    Response: {run_id, ticker, html_url, status}
    """
    result = await orchestrator.run_prompt_flow(request.ticker)
    return result

@app.get("/prompt/run/{run_id}/html")
async def get_html_result(run_id: str):
    """Retrieve HTML result for a prompt run."""
    # Query data-store for prompt_runs collection
    # Return HTML content
    pass

@app.get("/prompt/run/{run_id}/md")
async def get_md_result(run_id: str):
    """Retrieve Markdown result for a prompt run."""
    pass

@app.get("/prompt/run/{run_id}/json")
async def get_json_result(run_id: str):
    """Retrieve JSON result for a prompt run."""
    pass
```

##### 5.3 Integrate with Existing Services

**Prompt Template:**
- Use existing prompt templates from `prompt/` directory
- Template should include placeholders for:
  - `{ticker}` - Stock ticker symbol
  - `{company_data}` - Company financial data (from data-store)
  - `{context}` - Domain context (from prompt-manager)

**Example Template:**
```
Analyze the following stock:

Ticker: {ticker}

Company Data:
{company_data}

Context:
{context}

Provide a comprehensive analysis including:
1. Valuation assessment
2. Financial health
3. Growth prospects
4. Risk factors
5. Investment recommendation
```

##### 5.4 Data Storage Schema

**Collection**: `prompt_runs`

**Document Structure:**
```json
{
  "key": "prompt_run:uuid-here",
  "data": {
    "run_id": "uuid-here",
    "ticker": "AAPL",
    "company_key": "company:AAPL:2025-12-13T11:30:00",  // Reference to seed_companies document
    "prompt_template": "...",
    "filled_prompt": "...",
    "sanitized_prompt": "...",
    "llm_response_raw": "...",
    "llm_response_md": "...",
    "llm_response_html": "<html>...</html>",
    "llm_response_json": {...},
    "company_data": {...},  // Snapshot of company data used in prompt
    "metadata": {
      "model_used": "mock",
      "timestamp": "2025-12-13T...",
      "status": "completed",
      "context_files_loaded": ["biotech/01-introduction.md"]
    }
  },
  "metadata": {
    "source": "stock_miniapp",
    "ticker": "AAPL",
    "created_at": "2025-12-13T...",
    "updated_at": "2025-12-13T..."
  }
}
```

**Linking Prompt Results with Company Data:**

Since `prompt_runs` and `seed_companies` are in different collections, use one of these approaches:

**Approach 1: Query by Ticker (Recommended)**
- Both collections store `ticker` field
- Query both collections separately and combine in application code
- Simple, no schema changes needed

**Query Pattern:**
```python
# Get company data from seed_companies
company_result = data_store.query(
    collection="seed_companies",
    filters={"data.ticker": "AAPL"},
    sort={"stored_at": -1},  # Get latest
    limit=1
)
company_data = company_result.items[0].data if company_result.items else None

# Get prompt runs for same ticker
prompt_result = data_store.query(
    collection="prompt_runs",
    filters={"data.ticker": "AAPL"},
    sort={"metadata.created_at": -1},  # Most recent first
    limit=10
)
prompt_runs = prompt_result.items

# Combine in application
combined = {
    "company": company_data,
    "analyses": [run.data for run in prompt_runs]
}
```

**Approach 2: Store Company Key Reference**
- Store `company_key` in `prompt_runs` document (see schema above)
- Allows direct lookup of the exact company document used
- Useful when multiple company entries exist for same ticker

**Implementation:**
```python
# In orchestrator, when storing prompt run:
company_key = f"company:{ticker}:{company_data.get('extractedAt', datetime.now())}"

stored_key = await self._store_prompt_run(
    run_id=run_id,
    ticker=ticker,
    company_key=company_key,  # Store reference
    sanitized_prompt=sanitized_prompt,
    llm_response=llm_response
)

# Later, retrieve company by key:
company = data_store.retrieve(key=company_key, collection="seed_companies")
```

**Approach 3: Store Run IDs in Company Document (Bidirectional)**
- Add `prompt_run_ids` array to `seed_companies` documents
- Allows finding all analyses for a company
- Requires updating company document when prompt runs

**Implementation:**
```python
# After storing prompt run, update company document:
company_key = f"company:{ticker}:{timestamp}"
data_store.update(
    key=company_key,
    collection="seed_companies",
    data={
        "$push": {"metadata.prompt_run_ids": run_id}  # Add run_id to array
    }
)

# Query company with all its analyses:
company = data_store.retrieve(key=company_key, collection="seed_companies")
run_ids = company.metadata.get("prompt_run_ids", [])

# Fetch all prompt runs:
analyses = []
for run_id in run_ids:
    run = data_store.query(
        collection="prompt_runs",
        filters={"data.run_id": run_id},
        limit=1
    )
    if run.items:
        analyses.append(run.items[0].data)
```

**Recommended Approach:**

**For v1 (Simple):** Use **Approach 1** (query by ticker) ✅ **SELECTED FOR IMPLEMENTATION**
- No schema changes needed
- Works immediately
- Simple to implement
- Both collections already have `ticker` field

**For v2 (Enhanced):** Use **Approach 2** (store company_key) - **KEPT FOR FUTURE**
- More precise linking
- Handles multiple company entries per ticker
- Minimal schema change (add `company_key` field)
- Documented for future enhancement

**For v3 (Bidirectional):** Use **Approach 3** (store run_ids array) - **KEPT FOR FUTURE**
- Bidirectional linking
- Allows finding all analyses for a company
- Requires updating company document
- Documented for future enhancement

**API Endpoint for Reconnection:**

```python
@app.get("/prompt/run/{run_id}/with-company")
async def get_prompt_run_with_company(run_id: str):
    """
    Retrieve prompt run with associated company data.
    
    Queries both collections and combines results.
    """
    # Get prompt run
    prompt_run = await get_prompt_run(run_id)
    
    # Get company data by ticker
    ticker = prompt_run["data"]["ticker"]
    company_result = await data_store.query(
        collection="seed_companies",
        filters={"data.ticker": ticker},
        sort={"stored_at": -1},
        limit=1
    )
    
    company_data = company_result["items"][0]["data"] if company_result["items"] else None
    
    return {
        "run_id": run_id,
        "prompt_run": prompt_run["data"],
        "company": company_data,
        "ticker": ticker
    }
```

##### 5.5 REST API Call Chain (Detailed)

**Step-by-Step Flow:**
```
1. UI → POST /api/prompt/run
   Body: {ticker: "AAPL"}
   
2. Orchestrator → GET data-store /retrieve/{key}
   Query: Find company by ticker in seed_companies
   Response: {company data with valuation, financials, profitability}
   
3. Orchestrator → POST prompt-manager /prompt/load-contexts
   Body: {context_paths: ["biotech/01-introduction.md", ...]}
   Response: {contexts: [...]}
   
4. Orchestrator → POST prompt-manager /prompt/fill
   Body: {
     template_content: "...",
     params: {
       ticker: "AAPL",
       company_data: {...},
       context: "..."
     }
   }
   Response: {filled_prompt: "..."}
   
5. Orchestrator → POST prompt-security /validate (optional)
   Body: {prompt: "..."}
   Response: {sanitized_prompt: "...", is_safe: true}
   
6. Orchestrator → POST llm-provider /generate (port 8001)
   Body: {
     prompt: "...",
     provider: "mock",  # or "openai", "anthropic", "bedrock", etc.
     model: "mock-model",
     use_mock: true,  # Force mock mode (overrides provider)
     ticker: "AAPL"  # Optional context for mock provider
   }
   Response: {
     success: true,
     content: "...",
     provider: "mock",
     model: "mock-model",
     tokens_used: 100,
     cost: 0.0
   }
   
7. Orchestrator → POST data-store /store
   Body: {
     key: "prompt_run:uuid",
     data: {run_id, ticker, prompt, response_raw, ...},
     collection: "prompt_runs"
   }
   Response: {key: "prompt_run:uuid", success: true}
   
8. Orchestrator → POST format-converter /convert
   Body: {
     content: "...",
     from_format: "markdown",
     to_format: "html"
   }
   Response: {html: "<html>...</html>", md: "...", json: {...}}
   
9. Orchestrator → PUT data-store /update/{key}
   Body: {
     data: {llm_response_html: "...", llm_response_md: "...", ...}
   }
   Response: {success: true}
   
10. Orchestrator → UI
    Response: {
      success: true,
      run_id: "uuid",
      ticker: "AAPL",
      html_url: "/prompt/run/uuid/html",
      status: "completed"
    }
```

##### 5.4 Rendering HTML/MD/JSON Results

**Overview:**
After the orchestrator completes the prompt flow, the UI needs to display the rendered HTML, Markdown, and JSON formats. The orchestrator stores all formats in MongoDB and provides endpoints to retrieve them. All operations are logged with `run_id` for traceability.

**Backend Implementation (Orchestrator Endpoints):**

**Location**: `_dev/stock-miniapp/api/orchestrator_service.py`

**Key Features:**
- Three endpoints: `/prompt/run/{run_id}/html`, `/md`, `/json`
- Query MongoDB via data-store API to retrieve stored formats
- Proper Content-Type headers for each format
- Comprehensive logging with `run_id` context
- Environment-aware logging (DEBUG in dev, INFO in prod)

**Implementation Pattern:**

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse
import httpx
import logging
import os

# Configure logging based on environment
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)

# Detailed logging in dev/debug mode (removable in prod)
if DEBUG_MODE or ENVIRONMENT == "development":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] [run_id=%(run_id)s] %(name)s: %(message)s'
    )
else:
    # Production: minimal logging, no sensitive data
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )

@app.get("/prompt/run/{run_id}/html", response_class=HTMLResponse)
async def get_html_result(run_id: str):
    """Retrieve HTML result. All logs include run_id for traceability."""
    logger.info(f"Retrieving HTML result", extra={"run_id": run_id})
    
    try:
        async with httpx.AsyncClient() as client:
            query_response = await client.post(
                f"{DATA_STORE_URL}/query",
                json={
                    "collection": "prompt_runs",
                    "filters": {"data.run_id": run_id},
                    "limit": 1
                }
            )
            
            if query_response.status_code != 200:
                logger.error(f"Failed to query data-store", extra={"run_id": run_id})
                raise HTTPException(status_code=500, detail="Failed to retrieve prompt run")
            
            items = query_response.json().get("items", [])
            if not items:
                logger.warning(f"Prompt run not found", extra={"run_id": run_id})
                raise HTTPException(status_code=404, detail=f"Prompt run {run_id} not found")
            
            html_content = items[0].get("data", {}).get("llm_response_html")
            if not html_content:
                logger.warning(f"HTML content not available", extra={"run_id": run_id})
                raise HTTPException(status_code=404, detail=f"HTML not available for run {run_id}")
            
            logger.info(f"HTML retrieved successfully", extra={"run_id": run_id})
            return HTMLResponse(content=html_content)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error retrieving HTML: {str(e)}",
            extra={"run_id": run_id},
            exc_info=DEBUG_MODE  # Full traceback only in debug mode
        )
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Similar implementations for /md and /json endpoints
```

**Orchestrator Logging with Run ID:**

All orchestrator steps must log with the same `run_id` for end-to-end traceability:

```python
# In orchestrator.py - Every step uses same run_id
class PromptOrchestrator:
    async def run_prompt_flow(self, ticker: str) -> Dict[str, Any]:
        run_id = str(uuid.uuid4())
        log_extra = {"run_id": run_id, "ticker": ticker}
        
        logger.info(f"Starting prompt flow", extra=log_extra)
        
        try:
            # Step 1: Fetch company data
            logger.debug(f"Step 1: Fetching company data", extra=log_extra)
            company_data = await self._fetch_company_data(ticker)
            logger.debug(f"Step 1: Company data retrieved", extra=log_extra)
            
            # Step 2: Load context files
            logger.debug(f"Step 2: Loading context files", extra=log_extra)
            contexts = await self._load_contexts()
            logger.debug(f"Step 2: Context files loaded", extra=log_extra)
            
            # Step 3-8: All steps log with same run_id
            # ... (similar pattern for all steps)
            
            logger.info(f"Prompt flow completed successfully", extra=log_extra)
            return {"success": True, "run_id": run_id, ...}
            
        except Exception as e:
            logger.error(
                f"Prompt flow failed: {str(e)}",
                extra=log_extra,
                exc_info=DEBUG_MODE  # Full traceback only in debug
            )
            return {"success": False, "run_id": run_id, "error": str(e)}
```

**Logging Configuration:**

**Environment Variables:**
```bash
# Development/Debug (detailed logging, removable in prod)
DEBUG=true
ENVIRONMENT=development
LOG_LEVEL=DEBUG

# Production (minimal logging, no sensitive data)
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=INFO
```

**Log Levels:**
- **DEBUG**: Step-by-step details (dev only, can be removed in prod)
- **INFO**: Key milestones (start, completion, errors)
- **WARNING**: Non-critical issues
- **ERROR**: Failures with context

**Frontend Implementation (React Modal):**

**Location**: `_dev/stock-miniapp/web/client/src/PromptResultModal.js`

**Features:**
- Tabbed interface (HTML, Markdown, JSON tabs)
- Lazy loading (loads format only when tab clicked)
- HTML rendered with `dangerouslySetInnerHTML` in container
- Markdown/JSON displayed in `<pre>` tags
- Error handling and loading states
- "Open in New Tab" option for HTML

**Integration in App.js:**
```javascript
// Handle analyze button - receives run_id from orchestrator
const handleAnalyzePrompt = async (ticker) => {
  const response = await fetch('/api/prompt/run', {
    method: 'POST',
    body: JSON.stringify({ ticker })
  });
  const result = await response.json();
  
  if (result.success) {
    setSelectedRunId(result.run_id);  // Store run_id for modal
    setShowPromptModal(true);
  }
};

// Modal fetches formats using run_id
<PromptResultModal
  runId={selectedRunId}
  ticker={selectedTicker}
  onClose={() => setShowPromptModal(false)}
/>
```

**Response Formats:**
- **HTML**: `text/html` - Full HTML document with CSS
- **Markdown**: `text/markdown` - Plain text markdown
- **JSON**: `application/json` - Structured JSON object

**Error Handling:**
- **404**: Run ID not found → User-friendly error message
- **500**: Server error → Logged with run_id, generic error to user
- **Missing format**: Format not available → Show message, allow other formats

**Orchestrator Logging with Run ID:**

All orchestrator methods include `run_id` in logging context:

```python
# Every step logs with run_id
log_extra = {"run_id": run_id, "ticker": ticker}
logger.debug(f"Step 1: Fetching company data", extra=log_extra)
logger.info(f"Step 5: Generating LLM response", extra=log_extra)
logger.error(f"Prompt flow failed", extra=log_extra, exc_info=DEBUG_MODE)
```

**Logging Configuration:**

- **Development**: `DEBUG=true`, `LOG_LEVEL=DEBUG` - Detailed step-by-step logging
- **Production**: `DEBUG=false`, `LOG_LEVEL=INFO` - Key milestones only
- **Run ID Tracking**: All logs include `run_id` for end-to-end traceability
- **Exception Details**: Full tracebacks only in debug mode (`exc_info=DEBUG_MODE`)

**Frontend Implementation (React Modal):**

**Location**: `_dev/stock-miniapp/web/client/src/PromptResultModal.js`

**Features:**
- Tabbed interface (HTML, Markdown, JSON)
- Lazy loading (loads format on tab click)
- HTML rendered with `dangerouslySetInnerHTML`
- Markdown/JSON displayed in `<pre>` tags
- Error handling and loading states
- "Open in New Tab" option for HTML

**Integration:**
- Modal triggered from "Analyze" button in company table
- Receives `run_id` from orchestrator response
- Fetches formats from orchestrator endpoints via proxy

#### Files to Create/Modify

**Backend (stock-miniapp orchestrator):**
- `_dev/stock-miniapp/api/orchestrator.py` - Orchestrator class with run_id logging
- `_dev/stock-miniapp/api/orchestrator_service.py` - FastAPI service with format endpoints
- `_dev/stock-miniapp/api/requirements.txt` - Python dependencies (httpx, fastapi, etc.)
- `_dev/stock-miniapp/api/.env.example` - Environment variables (DEBUG, LOG_LEVEL, ENVIRONMENT)

**Frontend (React UI):**
- `_dev/stock-miniapp/web/client/src/App.js` - Add "Analyze" button and modal integration
- `_dev/stock-miniapp/web/client/src/PromptResultModal.js` - Modal component for displaying results
- `_dev/stock-miniapp/web/client/src/PromptResultModal.css` - Styles for modal and content display
- `_dev/stock-miniapp/web/client/src/App.css` - Styles for button

**Integration:**
- `_dev/stock-miniapp/web/server.js` - Add proxy route for `/api/prompt/*`

#### Testing Plan

1. **Unit Test**: Test orchestrator methods individually
2. **Integration Test**: Test full flow with all services running
3. **UI Test**: Test button click → loading → result display
4. **Error Test**: Test error handling (service down, invalid ticker, etc.)
5. **Mock Test**: Verify mock LLM provider is used correctly

#### Success Criteria

- ✅ "Analyze" button added to each row in company table
- ✅ Button triggers orchestrator endpoint
- ✅ Orchestrator coordinates all microservices correctly
- ✅ Prompt template filled with ticker + company data
- ✅ LLM response generated (mock mode)
- ✅ Response stored in MongoDB `prompt_runs` collection
- ✅ HTML/MD/JSON rendered via format-converter
- ✅ Rendered formats stored in MongoDB
- ✅ UI displays HTML result in modal/new page
- ✅ Error handling works (service failures, invalid data)
- ✅ All services integrated (prompt-manager, prompt-security, llm-provider, data-store, format-converter)

#### Dependencies

**Required Services:**
- data-store (port 8007) - Company data retrieval and prompt storage
- prompt-manager (port 8000) - Template loading and filling
- format-converter (port 8004) - HTML/MD/JSON rendering
- prompt-security (port 8002) - Optional, graceful degradation if unavailable

**Required Services:**
- llm-provider (port 8001) - Response generation (REST API service with provider swapping)
  - Supports provider swapping via request parameters or environment variables
  - Default: mock provider for v1 (use_mock=true)
  - Can switch to OpenAI, Anthropic, Bedrock, etc. via configuration

**Python Dependencies:**
- `fastapi>=0.104.0` - Orchestrator API
- `uvicorn[standard]>=0.24.0` - ASGI server
- `httpx>=0.25.0` - HTTP client for service calls
- `pydantic>=2.0.0` - Request/response validation
- `llm-provider` (from `_dev/llm-provider`) - LLM provider library (for MockProvider)

#### Notes

- **Orchestrator Pattern**: Centralizes workflow logic, simplifies UI, enables monitoring
- **Mock LLM**: First iteration uses mock provider; design is pluggable for Bedrock later
- **Error Handling**: Orchestrator handles service failures gracefully
- **Future Extensions**: Easy to add caching, retries, rate limiting, etc.
- **UI Autocomplete**: Postponed to future iteration; current flow starts from table  
### Step 6: Periodic Materialization Job (Optional)

#### Overview
Create a background job that regenerates MD/HTML/JSON formats from stored prompt responses without re-running the LLM. This is useful when:
- Format-converter is updated with new rendering features
- HTML templates are improved
- Need to regenerate formats for historical data

#### Architecture

```
┌─────────────────────────────────────────────────────────┐
│         Periodic Materialization Job                    │
│         (Python Script / Cron / Scheduled Task)         │
└─────────────────────────────────────────────────────────┘
                    │
                    │ Query prompt_runs collection
                    ▼
        ┌───────────────────────────┐
        │   data-store              │
        │   (Port 8007)             │
        │                           │
        │ POST /query               │
        │ Filters:                  │
        │ - status: "completed"     │
        │ - llm_response_html: null │
        │   OR updated_at < job_run │
        └───────────────────────────┘
                    │
                    │ For each prompt_run:
                    ▼
        ┌───────────────────────────┐
        │   format-converter         │
        │   (Port 8004)              │
        │                           │
        │ POST /convert             │
        │ Input: llm_response_md    │
        │ Output: HTML, JSON        │
        └───────────────────────────┘
                    │
                    │ Update prompt_runs
                    ▼
        ┌───────────────────────────┐
        │   data-store              │
        │   (Port 8007)             │
        │                           │
        │ PUT /update/{key}         │
        │ Update: llm_response_html │
        │        llm_response_json  │
        └───────────────────────────┘
```

#### Implementation

**Location**: `_dev/stock-miniapp/scripts/materialize_formats.py`

**Job Flow:**
1. Query `prompt_runs` collection for completed runs
2. Filter: runs without HTML or runs older than last materialization
3. For each run:
   - Extract `llm_response_md` or `llm_response_raw`
   - Call format-converter to generate HTML/JSON
   - Update prompt_runs document with new formats
4. Log results and metrics

**Scheduling Options:**
- **Cron**: Run daily/weekly via system cron
- **Python scheduler**: Use `schedule` library for in-process scheduling
- **AWS EventBridge**: For cloud deployment
- **Manual**: CLI command for on-demand runs

**Example CLI:**
```bash
# Run materialization job
python scripts/materialize_formats.py --collection prompt_runs --dry-run

# Materialize specific run
python scripts/materialize_formats.py --run-id uuid-here

# Materialize all runs without HTML
python scripts/materialize_formats.py --missing-html-only
```

#### Files to Create

- `_dev/stock-miniapp/scripts/materialize_formats.py` - Main job script
- `_dev/stock-miniapp/scripts/requirements.txt` - Job dependencies
- `_dev/stock-miniapp/scripts/README.md` - Job documentation

#### Success Criteria

- ✅ Job queries prompt_runs collection correctly
- ✅ Identifies runs needing materialization
- ✅ Calls format-converter for each run
- ✅ Updates MongoDB with new formats
- ✅ Handles errors gracefully (skip failed runs, continue)
- ✅ Provides logging and metrics
- ✅ Can run manually or via scheduler

---

### Step 7: Hardening & Metrics

#### Overview
Ensure all services expose Prometheus metrics and integrate with centralized monitoring. Add basic dashboards for observability.

#### Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Prometheus (Port 9090)                      │
│         Scrapes metrics from all services                │
└─────────────────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┬───────────┐
        │           │           │           │
        ▼           ▼           ▼           ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ data-     │ │ prompt-  │ │ llm-     │ │ format-  │
│ retriever │ │ manager  │ │ provider │ │ converter│
│ :8003     │ │ :8000    │ │ :8001    │ │ :8004    │
│ /metrics  │ │ /metrics │ │ /metrics │ │ /metrics │
└──────────┘ └──────────┘ └──────────┘ └──────────┘
        │           │           │           │
        ▼           ▼           ▼           ▼
┌─────────────────────────────────────────────────────────┐
│              Grafana (Port 3000)                        │
│         Visualizes metrics and dashboards               │
└─────────────────────────────────────────────────────────┘
```

#### Metrics to Expose

**Orchestrator Metrics:**
- `stock_miniapp_prompt_runs_total` - Total prompt runs (by status: success, failed)
- `stock_miniapp_prompt_duration_seconds` - Duration histogram
- `stock_miniapp_orchestrator_errors_total` - Error counts (by service)
- `stock_miniapp_service_calls_total` - Service call counts (by service, status)

**Service Metrics (Already Exposed):**
- data-retriever: Operations, cache hits, errors
- prompt-manager: Token usage, validation counts
- llm-provider: Generation counts, latency
- format-converter: Conversion counts, errors
- data-store: CRUD operations, query performance

#### Implementation

**Orchestrator Metrics:**
- Add Prometheus client to orchestrator service
- Track workflow metrics (duration, success/failure)
- Track service call metrics (which services called, success/failure)
- Expose `/metrics` endpoint

**Grafana Dashboard:**
- Create dashboard for stock-miniapp
- Panels:
  - Prompt runs over time (success vs failed)
  - Average prompt duration
  - Service call distribution
  - Error rates by service
  - Most analyzed tickers

**Files to Create/Modify:**
- `_dev/stock-miniapp/api/orchestrator.py` - Add metrics collection
- `_dev/stock-miniapp/api/orchestrator_service.py` - Add `/metrics` endpoint
- `_dev/monitoring/grafana/dashboards/stock-miniapp.json` - Dashboard definition

#### Success Criteria

- ✅ Orchestrator exposes `/metrics` endpoint
- ✅ All workflow metrics tracked
- ✅ Service call metrics tracked
- ✅ Grafana dashboard created
- ✅ Metrics visible in Grafana
- ✅ Alerts configured (optional)

---

### Step 8: Swap LLM Provider to Bedrock (Future)

#### Overview
Replace mock LLM provider with AWS Bedrock, using configuration only (no flow changes). This demonstrates the pluggable architecture.

#### Architecture Change

```
Current (Step 5):
┌──────────────┐
│ Orchestrator │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ llm-provider │
│ (Mock Mode)  │
└──────────────┘

Future (Step 8):
┌──────────────┐
│ Orchestrator │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ llm-provider │
│ (Bedrock)    │
│              │
│ Config:      │
│ - model:     │
│   claude-3   │
│ - region:    │
│   us-east-1  │
│ - use_mock:  │
│   false      │
└──────────────┘
       │
       ▼
┌──────────────┐
│ AWS Bedrock  │
│ API          │
└──────────────┘
```

#### Configuration Strategy

**Environment Variables:**
```bash
# _dev/llm-provider/.env
LLM_PROVIDER_BACKEND=bedrock  # or "mock", "openai", "litellm"
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_REGION=us-east-1
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
USE_MOCK=false
```

**Orchestrator Configuration:**
```python
# No changes needed - orchestrator calls llm-provider API
# llm-provider handles backend selection internally
```

**Flow Remains Identical:**
- Orchestrator still calls `POST /llm-provider/generate`
- Request body unchanged: `{prompt: "...", model: "claude-3", use_mock: false}`
- Response format unchanged: `{response: "...", model: "claude-3"}`
- Only backend changes (mock → Bedrock)

#### Implementation Steps

1. **Configure llm-provider:**
   - Add Bedrock provider implementation (if not exists)
   - Update `.env` to use Bedrock
   - Test Bedrock connection

2. **Update orchestrator config:**
   - Set `use_mock: false` in orchestrator request
   - No code changes needed

3. **Test:**
   - Run prompt flow with Bedrock
   - Verify responses stored correctly
   - Check metrics and monitoring

#### Files to Modify

- `_dev/llm-provider/.env` - Change backend configuration
- `_dev/stock-miniapp/api/orchestrator.py` - Set `use_mock: false` (or from config)

#### Success Criteria

- ✅ Bedrock provider configured
- ✅ Prompt flow works with Bedrock
- ✅ Responses stored correctly
- ✅ No flow changes required
- ✅ Metrics track Bedrock usage
- ✅ Error handling works (rate limits, timeouts)

#### Notes

- **Pluggable Design**: Architecture supports provider swap via configuration
- **No Flow Changes**: Orchestrator and UI unchanged
- **Cost Considerations**: Bedrock usage will incur AWS costs
- **Rate Limits**: Bedrock has rate limits; implement retry logic
- **Monitoring**: Track Bedrock API calls, latency, costs  

Please review and adjust before we implement.

