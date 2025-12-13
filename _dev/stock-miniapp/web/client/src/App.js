import React, { useState } from 'react';
import './App.css';

function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [count, setCount] = useState(100);

  const handleSeedCompanies = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    // Create timeout controller
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 minute timeout

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
      setResult(data);
    } catch (err) {
      if (err.name === 'AbortError') {
        setError('Request timed out. The operation may still be processing. Please check MongoDB or try again with a smaller count.');
      } else {
        setError(err.message || 'Failed to seed companies');
      }
    } finally {
      clearTimeout(timeoutId);
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Stock Mini-App - Admin Panel</h1>
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
              disabled={loading}
            />
          </div>

          <button
            onClick={handleSeedCompanies}
            disabled={loading}
            className="seed-button"
          >
            {loading ? 'Seeding...' : `Seed ${count} Companies`}
          </button>

          {error && (
            <div className="error-message">
              <strong>Error:</strong> {error}
            </div>
          )}

          {result && (
            <div className="success-message">
              <h3>✅ Success!</h3>
              <ul>
                <li>Companies stored: <strong>{result.records_loaded}</strong></li>
                <li>Total in collection: <strong>{result.total_in_collection}</strong></li>
                <li>Collection: <strong>{result.collection}</strong></li>
                {result.errors && result.errors.length > 0 && (
                  <li>Errors: <strong>{result.errors.length}</strong></li>
                )}
              </ul>
              {result.keys && result.keys.length > 0 && (
                <details>
                  <summary>Sample Keys (first 10)</summary>
                  <ul>
                    {result.keys.map((key, idx) => (
                      <li key={idx}>{key}</li>
                    ))}
                  </ul>
                </details>
              )}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;

