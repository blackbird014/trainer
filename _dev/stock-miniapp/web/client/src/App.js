import React, { useState, useEffect } from 'react';
import './App.css';
import PromptResultModal from './PromptResultModal';
import CollectionExplorer from './components/CollectionExplorer';

// Reusable table component
function CompanyTable({ companies, onAnalyze }) {
  if (!companies || companies.length === 0) {
    return <p>No companies to display.</p>;
  }

  // Format date for display
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      const date = new Date(dateString);
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (e) {
      return dateString;
    }
  };

  return (
    <div className="table-container">
      <table className="company-table">
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Retrieved</th>
            <th>Market Cap</th>
            <th>Revenue</th>
            <th>Profit Margin</th>
            <th>P/E Ratio</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {companies.map((company, idx) => {
            const data = company.data || company;
            const valuation = data.valuation || {};
            const financials = data.financials || {};
            const profitability = data.profitability || {};
            
            // Get retrieval date from extractedAt or stored_at
            const retrievalDate = data.extractedAt || company.stored_at || company.updated_at;
            
            return (
              <tr key={idx}>
                <td>{data.ticker || 'N/A'}</td>
                <td>{formatDate(retrievalDate)}</td>
                <td>{valuation.marketCap || 'N/A'}</td>
                <td>{financials.revenue || 'N/A'}</td>
                <td>{profitability.profitMargin || 'N/A'}</td>
                <td>{valuation.trailingPE || 'N/A'}</td>
                <td>
                  <button
                    className="analyze-button"
                    onClick={() => onAnalyze(data.ticker || '')}
                    disabled={!data.ticker}
                  >
                    Analyze
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function App() {
  const [seedLoading, setSeedLoading] = useState(false);
  const [seedResult, setSeedResult] = useState(null);
  const [seedError, setSeedError] = useState(null);
  const [count, setCount] = useState(100);

  const [scrapeLoading, setScrapeLoading] = useState(false);
  const [scrapeError, setScrapeError] = useState(null);
  const [tickers, setTickers] = useState('');
  const [companies, setCompanies] = useState([]);

  // Prompt flow state
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzeError, setAnalyzeError] = useState(null);
  const [promptResult, setPromptResult] = useState(null);
  const [showModal, setShowModal] = useState(false);

  // DB Viewer state
  const [showDBViewer, setShowDBViewer] = useState(false);

  // Load last 10 companies on mount and after operations
  // Only show the latest entry for each ticker
  const loadLastCompanies = async () => {
    try {
      // Get more items to ensure we have enough after deduplication
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          collection: 'seed_companies',
          filters: {},
          limit: 100, // Get more to filter duplicates
          sort: { stored_at: -1 }, // Most recent first
          offset: 0
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const items = data.items || [];
        
        // Deduplicate by ticker - keep only the latest (first in sorted list)
        const tickerMap = new Map();
        items.forEach(item => {
          const ticker = (item.data?.ticker || item.ticker || '').toUpperCase();
          if (ticker && !tickerMap.has(ticker)) {
            tickerMap.set(ticker, item);
          }
        });
        
        // Convert map to array and take first 10
        const uniqueCompanies = Array.from(tickerMap.values()).slice(0, 10);
        setCompanies(uniqueCompanies);
      }
    } catch (err) {
      console.error('Failed to load companies:', err);
    }
  };

  useEffect(() => {
    loadLastCompanies();
  }, []);

  const handleSeedCompanies = async () => {
    setSeedLoading(true);
    setSeedError(null);
    setSeedResult(null);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 120000);

    try {
      const response = await fetch('/api/admin/seed-companies', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          count: count,
          collection: 'seed_companies'
        }),
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to seed companies');
      }

      const data = await response.json();
      setSeedResult(data);
      await loadLastCompanies(); // Refresh table
    } catch (err) {
      if (err.name === 'AbortError') {
        setSeedError('Request timed out. The operation may still be processing. Please check MongoDB or try again with a smaller count.');
      } else {
        setSeedError(err.message || 'Failed to seed companies');
      }
    } finally {
      clearTimeout(timeoutId);
      setSeedLoading(false);
    }
  };

  const handleScrapeTickers = async () => {
    setScrapeLoading(true);
    setScrapeError(null);

    // Parse tickers (comma-separated or space-separated)
    const tickerList = tickers
      .split(/[,\s]+/)
      .map(t => t.trim().toUpperCase())
      .filter(t => t.length > 0);

    if (tickerList.length === 0) {
      setScrapeError('Please enter at least one ticker symbol');
      setScrapeLoading(false);
      return;
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 120000);

    try {
      // Step 1: Retrieve data from data-retriever
      const retrieveResponse = await fetch('/api/retrieve', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          source: 'yahoo_finance',
          query: {
            tickers: tickerList,
            use_mock: false // Can be made configurable
          }
        }),
        signal: controller.signal,
      });

      if (!retrieveResponse.ok) {
        const errorData = await retrieveResponse.json();
        throw new Error(errorData.error || 'Failed to retrieve data');
      }

      const retrieveData = await retrieveResponse.json();
      
      if (!retrieveData.success) {
        throw new Error(retrieveData.error || 'Failed to retrieve data');
      }
      
      if (!retrieveData.data) {
        throw new Error('No data in response');
      }

      // Step 2: Transform and persist to data-store
      // Handle both single ticker and batch formats
      let tickerData;
      if (retrieveData.data.tickers) {
        // Batch format: {tickers: [...]}
        tickerData = retrieveData.data.tickers;
      } else if (retrieveData.data.ticker) {
        // Single ticker format: {ticker: "...", ...}
        tickerData = [retrieveData.data];
      } else {
        throw new Error('Unexpected data format in response');
      }
      const now = new Date().toISOString();
      
      const items = tickerData.map(tickerData => {
        const ticker = tickerData.ticker || tickerList[0];
        return {
          key: `company:${ticker}:${now}`,
          data: tickerData,
          metadata: {
            source: 'yahoo_finance',
            ticker: ticker,
            extracted_at: tickerData.extractedAt || now
          }
        };
      });

      // Step 3: Store in seed_companies collection
      const storeResponse = await fetch('/api/bulk_store', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          items: items,
          collection: 'seed_companies'
        }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!storeResponse.ok) {
        const errorData = await storeResponse.json();
        throw new Error(errorData.detail || 'Failed to store data');
      }

      // Step 4: Refresh table
      await loadLastCompanies();
      
    } catch (err) {
      if (err.name === 'AbortError') {
        setScrapeError('Request timed out. The operation may still be processing.');
      } else {
        setScrapeError(err.message || 'Failed to scrape tickers');
      }
    } finally {
      clearTimeout(timeoutId);
      setScrapeLoading(false);
    }
  };

  // Handle prompt analysis
  const handleAnalyzePrompt = async (ticker) => {
    if (!ticker) {
      setAnalyzeError('Ticker is required');
      return;
    }

    setAnalyzing(true);
    setAnalyzeError(null);
    setPromptResult(null);

    try {
      const response = await fetch('/api/prompt/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ticker }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || errorData.detail || 'Failed to run prompt flow');
      }

      const result = await response.json();
      
      console.log('Prompt flow result:', result); // Debug log
      
      if (result.success) {
        setPromptResult(result);
        setShowModal(true);
        console.log('Modal should open with runId:', result.run_id); // Debug log
      } else {
        // Even on failure, show the error in modal if we have a run_id
        if (result.run_id) {
          setPromptResult(result);
          setShowModal(true);
          setAnalyzeError(result.error || 'Prompt flow failed');
        } else {
          throw new Error(result.error || 'Prompt flow failed');
        }
      }
    } catch (err) {
      setAnalyzeError(err.message);
      console.error('Error analyzing prompt:', err);
    } finally {
      setAnalyzing(false);
    }
  };

  // Show DB Viewer if requested
  if (showDBViewer) {
    return (
      <CollectionExplorer onBack={() => setShowDBViewer(false)} />
    );
  }

  return (
    <div className="App">
      <header className="App-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1>Stock Mini-App - Admin Panel</h1>
          <button
            onClick={() => setShowDBViewer(true)}
            style={{
              background: 'white',
              color: '#282c34',
              border: 'none',
              padding: '10px 20px',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: 'bold'
            }}
          >
            View Database Collections
          </button>
        </div>
      </header>

      <main className="App-main">
        <section className="seed-section">
          <h2>Seed Companies</h2>
          <p>Generate and store fake company data in MongoDB.</p>
          
          <div className="form-group">
            <label htmlFor="count">Number of companies:</label>
            <input
              id="count"
              type="number"
              min="1"
              max="1000"
              value={count}
              onChange={(e) => setCount(parseInt(e.target.value) || 100)}
              disabled={seedLoading}
            />
          </div>

          <button
            onClick={handleSeedCompanies}
            disabled={seedLoading}
            className="seed-button"
          >
            {seedLoading ? 'Seeding...' : `Seed ${count} Companies`}
          </button>

          {seedError && (
            <div className="error-message">
              <strong>Error:</strong> {seedError}
            </div>
          )}

          {seedResult && (
            <div className="success-message">
              <h3>✅ Success!</h3>
              <ul>
                <li>Companies stored: <strong>{seedResult.records_loaded}</strong></li>
                <li>Total in collection: <strong>{seedResult.total_in_collection}</strong></li>
                <li>Collection: <strong>{seedResult.collection}</strong></li>
              </ul>
            </div>
          )}
        </section>

        <section className="scrape-section">
          <h2>Scrape Yahoo Finance Data</h2>
          <p>Retrieve real stock data from Yahoo Finance and store in MongoDB.</p>
          
          <div className="form-group">
            <label htmlFor="tickers">Ticker symbols (comma or space separated):</label>
            <input
              id="tickers"
              type="text"
              placeholder="AAPL, MSFT, GOOGL"
              value={tickers}
              onChange={(e) => setTickers(e.target.value)}
              disabled={scrapeLoading}
            />
          </div>

          <button
            onClick={handleScrapeTickers}
            disabled={scrapeLoading}
            className="scrape-button"
          >
            {scrapeLoading ? 'Scraping...' : 'Scrape Tickers'}
          </button>

          {scrapeError && (
            <div className="error-message">
              <strong>Error:</strong> {scrapeError}
            </div>
          )}
        </section>

        <section className="table-section">
          <h2>Last 10 Companies</h2>
          <p>Most recently added companies (seed or scraped).</p>
          <CompanyTable companies={companies} onAnalyze={handleAnalyzePrompt} />
          
          {analyzing && (
            <div className="analyzing-message">
              <strong>Analyzing...</strong> This may take 10-20 seconds.
            </div>
          )}

          {analyzeError && (
            <div className="error-message">
              <strong>Error:</strong> {analyzeError}
            </div>
          )}
        </section>
      </main>

      {/* Prompt Result Modal */}
      <PromptResultModal
        isOpen={showModal}
        onClose={() => {
          setShowModal(false);
          setPromptResult(null);
        }}
        runId={promptResult?.run_id}
        ticker={promptResult?.ticker}
      />
    </div>
  );
}

export default App;
