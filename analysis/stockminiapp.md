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
- Scraped entries: JSON shaped like the Yahoo metrics in `prompt/scrape_tickers.md` (valuation, financials, profitability fields). Stored with `source: "yahoo_scrape"` and `ticker`.
- Prompt results: store `prompt`, `sanitized_prompt`, `llm_response_raw`, `llm_response_md`, `llm_response_html`, `metadata` (ticker, timestamp, model_used, run_id). Keep both MD and HTML variants for UI; HTML written by format-converter.

## Flows (with module calls and REST chains)
### A. Seed Data (Admin → data-store)
- REST chain: UI/trigger → POST data-store API `/bulk_store` (port 8007) with 100 generated company docs → data-store (Mongo) saves to `seed_companies` → response returns inserted keys/ids.

### B. Scrape Yahoo (Admin → data-retriever → data-store)
- REST chain: UI/trigger → POST data-retriever API `/retrieve` (port 8003) with `{"source":"yahoo_finance","query":{"tickers":[...]}}` → YahooFinanceRetriever (real or deterministic mock) → data-retriever persists to data-store `scraped_metrics` → response returns counts/sample.

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
- MongoDB via Docker; connection string `mongodb://localhost:27017`, DB `trainer_data`, collections: `seed_companies`, `scraped_metrics`, `prompt_runs`.  
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
- Collections ready: `seed_companies`, `scraped_metrics`, `prompt_runs`

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
### Step 4: Build minimal UI/endpoint to trigger scrape via data-retriever and show summary from data-store.  
### Step 5: Prompt flow v1 (mock LLM): prompt-manager + prompt-security + llm-provider mock; persist to data-store; render via format-converter; minimal UI page to run and view HTML.  
### Step 6: Optional periodic job: regenerate MD/HTML/JSON from stored prompt responses (format-converter) and persist.  
### Step 7: Hardening & metrics: ensure Prometheus metrics exposed from involved services; basic dashboards optional.  
### Step 8: Later (not in first iteration): swap llm-provider mock to Bedrock by configuration only; no flow changes.  

Please review and adjust before we implement.

