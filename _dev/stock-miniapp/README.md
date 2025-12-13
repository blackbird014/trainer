# Stock Mini-App

A demonstration mini-application that showcases the usage of existing modules (data-store, data-retriever, prompt-manager, prompt-security, llm-provider, format-converter) with MongoDB.

## Architecture

```
React UI (Browser) 
    ↓ HTTP POST /api/admin/seed-companies
Express Server (Port 3000) - Proxies API calls, serves React
    ↓ Proxy to FastAPI
FastAPI (Port 8007) - /admin/seed-companies endpoint (data-store API)
    ↓ Store via data-store module
MongoDB (Port 27017) - seed_companies collection
```

## Features

- **Seed Companies**: Generate and store fake company data in MongoDB via web UI
- **REST API**: All operations go through REST APIs (no direct database access from UI)
- **Multiple Triggers**: Can be triggered multiple times to add more companies

## Prerequisites

- Node.js (v14 or higher)
- npm (comes with Node.js)
- Python 3.8+
- MongoDB running (Docker container or local installation)
- data-store module dependencies installed

## Setup

### 1. Ensure MongoDB is Running

```bash
# Check if MongoDB container is running
docker ps | grep mongodb

# If not running, start it
cd _dev/data-store
./setup_mongodb.sh
```

### 2. Install Express Server Dependencies

```bash
cd _dev/stock-miniapp/web
npm install
```

### 3. Install React Client Dependencies

```bash
cd _dev/stock-miniapp/web/client
npm install
```

### 4. Build React Application

```bash
# Still in client directory
npm run build
```

This creates the production build in `client/build/` directory.

## Running the Application

### Step 1: Start data-store API (FastAPI)

In a terminal:

```bash
cd _dev/data-store
python api_service.py
```

The API will start on `http://localhost:8007`

You can verify it's running:
```bash
curl http://localhost:8007/health
```

### Step 2: Start Express Server

In another terminal:

```bash
cd _dev/stock-miniapp/web
npm start
```

The Express server will start on `http://localhost:3001` (port 3000 may be used by prompt-manager)

### Step 3: Access the Web UI

Open your browser and navigate to:
```
http://localhost:3001
```

**Note**: Port 3000 may be occupied by the prompt-manager Express app. The stock-miniapp uses port 3001 by default.

You should see the "Stock Mini-App - Admin Panel" with a form to seed companies.

## Usage

### Seed Companies

1. Enter the number of companies you want to generate (default: 100)
2. Click "Seed Companies" button
3. Wait for the operation to complete
4. View the results showing:
   - Number of companies stored
   - Total companies in collection
   - Sample keys

### Multiple Seeding

You can click the button multiple times to add more companies. Each time, new companies will be added to the existing collection.

## API Endpoints

The Express server proxies requests to the FastAPI backend:

- `POST /api/admin/seed-companies` - Seed fake companies
  ```json
  {
    "count": 100,
    "collection": "seed_companies"
  }
  ```

- `GET /api/health` - Health check
- `GET /api/` - API information

## Verification

### Check MongoDB

```bash
# Connect to MongoDB shell
docker exec mongodb mongosh trainer_data

# Count companies
db.seed_companies.countDocuments({})

# View a sample document
db.seed_companies.findOne()
```

### Check via API

```bash
# Query companies via data-store API
curl http://localhost:8007/query -X POST \
  -H "Content-Type: application/json" \
  -d '{"filters": {"metadata.source": "seed_data"}, "limit": 5}'
```

## Development

### React Development Mode

For React development with hot reload:

```bash
cd _dev/stock-miniapp/web/client
npm start
```

This runs React on `http://localhost:3001` (or next available port) with hot reload.

**Note**: In development mode, you'll need to update the Express server to proxy to the React dev server, or run both servers separately.

### Express Development Mode

For Express server with auto-reload:

```bash
cd _dev/stock-miniapp/web
npm run dev
```

Requires `nodemon` to be installed (included in devDependencies).

## Project Structure

```
stock-miniapp/
├── web/
│   ├── server.js              # Express server with API proxy
│   ├── package.json           # Express dependencies
│   └── client/                # React application
│       ├── src/
│       │   ├── App.js         # Main React component
│       │   ├── App.css        # Styles
│       │   ├── index.js       # React entry point
│       │   └── index.css      # Base styles
│       ├── public/
│       │   └── index.html     # HTML template
│       ├── build/             # Production build (generated)
│       └── package.json       # React dependencies
└── README.md                  # This file
```

## Troubleshooting

### MongoDB Connection Issues

- Ensure MongoDB container is running: `docker ps | grep mongodb`
- Check connection string: `mongodb://localhost:27017`
- Verify database exists: `trainer_data`

### API Connection Issues

- Ensure data-store API is running on port 8007
- Check Express server logs for proxy errors
- Verify API_URL in `server.js` matches your FastAPI port

### React Build Issues

- Ensure all dependencies are installed: `npm install`
- Clear build cache: `rm -rf client/build`
- Rebuild: `npm run build`

### Port Conflicts

- Express server: Change `PORT` in `server.js` or set `PORT` environment variable
- FastAPI: Change port in `api_service.py` or set `PORT` environment variable
- Update `API_URL` in `server.js` if FastAPI port changes

## Next Steps

This is Step 2 of the stock mini-app implementation. Future steps will include:

- Step 3: Yahoo Finance scraping integration
- Step 4: Scrape UI and summary display
- Step 5: Prompt flow with mock LLM
- Step 6: Periodic materialization job
- Step 7: Metrics and hardening

See `analysis/stockminiapp.md` for the complete specification.

## License

MIT

