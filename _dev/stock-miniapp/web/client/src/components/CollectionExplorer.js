import React, { useState, useEffect } from 'react';
import './CollectionExplorer.css';

function CollectionExplorer({ onBack }) {
  const [collections, setCollections] = useState([]);
  const [selectedCollection, setSelectedCollection] = useState('');
  const [filterJson, setFilterJson] = useState('{}');
  const [sortJson, setSortJson] = useState('{"stored_at": -1}');
  const [limit, setLimit] = useState(50);
  const [offset, setOffset] = useState(0);
  const [results, setResults] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expandedRows, setExpandedRows] = useState(new Set());

  // Load collections on mount
  useEffect(() => {
    loadCollections();
  }, []);

  // Load collections when selected collection changes
  useEffect(() => {
    if (selectedCollection) {
      loadData();
    } else {
      setResults([]);
      setTotalCount(0);
    }
  }, [selectedCollection, filterJson, sortJson, limit, offset]);

  const loadCollections = async () => {
    try {
      const response = await fetch('/api/collections');
      if (!response.ok) {
        throw new Error('Failed to load collections');
      }
      const data = await response.json();
      setCollections(data.collections || []);
      if (data.collections && data.collections.length > 0 && !selectedCollection) {
        setSelectedCollection(data.collections[0]);
      }
    } catch (err) {
      setError(`Failed to load collections: ${err.message}`);
    }
  };

  const loadData = async () => {
    if (!selectedCollection) return;

    setLoading(true);
    setError(null);

    try {
      // Parse filter and sort JSON
      let filter = {};
      let sort = {};
      
      try {
        filter = filterJson.trim() ? JSON.parse(filterJson) : {};
      } catch (e) {
        throw new Error(`Invalid filter JSON: ${e.message}`);
      }

      try {
        sort = sortJson.trim() ? JSON.parse(sortJson) : {};
      } catch (e) {
        throw new Error(`Invalid sort JSON: ${e.message}`);
      }

      // Fetch count
      const countResponse = await fetch('/api/count', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          collection: selectedCollection,
          filter: filter
        })
      });

      if (!countResponse.ok) {
        const errorData = await countResponse.json();
        throw new Error(errorData.error || errorData.detail || 'Failed to get count');
      }

      const countData = await countResponse.json();
      setTotalCount(countData.count || 0);

      // Fetch query results
      const queryResponse = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          collection: selectedCollection,
          filters: filter,
          sort: sort,
          limit: limit,
          offset: offset
        })
      });

      if (!queryResponse.ok) {
        const errorData = await queryResponse.json();
        throw new Error(errorData.error || errorData.detail || 'Failed to query data');
      }

      const queryData = await queryResponse.json();
      setResults(queryData.items || []);
    } catch (err) {
      setError(err.message);
      setResults([]);
      setTotalCount(0);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    loadData();
  };

  const toggleRowExpansion = (index) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedRows(newExpanded);
  };

  const formatValue = (value) => {
    if (value === null) return 'null';
    if (value === undefined) return 'undefined';
    if (typeof value === 'object') {
      return JSON.stringify(value, null, 2);
    }
    return String(value);
  };

  return (
    <div className="collection-explorer">
      <div className="explorer-header">
        <h1>Database Collection Explorer</h1>
        <button className="back-button" onClick={onBack}>
          ← Back to Main
        </button>
      </div>

      <div className="explorer-controls">
        <div className="control-group">
          <label htmlFor="collection-select">Collection:</label>
          <select
            id="collection-select"
            value={selectedCollection}
            onChange={(e) => {
              setSelectedCollection(e.target.value);
              setOffset(0); // Reset offset when collection changes
            }}
            disabled={loading}
          >
            <option value="">Select a collection...</option>
            {collections.map((col) => (
              <option key={col} value={col}>
                {col}
              </option>
            ))}
          </select>
        </div>

        <div className="control-group">
          <label htmlFor="filter-input">Filter (JSON):</label>
          <textarea
            id="filter-input"
            value={filterJson}
            onChange={(e) => {
              setFilterJson(e.target.value);
              setOffset(0); // Reset offset when filter changes
            }}
            placeholder='{"status": "active"}'
            rows={3}
            disabled={loading || !selectedCollection}
          />
        </div>

        <div className="control-group">
          <label htmlFor="sort-input">Sort (JSON):</label>
          <textarea
            id="sort-input"
            value={sortJson}
            onChange={(e) => {
              setSortJson(e.target.value);
              setOffset(0); // Reset offset when sort changes
            }}
            placeholder='{"stored_at": -1}'
            rows={2}
            disabled={loading || !selectedCollection}
          />
        </div>

        <div className="control-group inline-controls">
          <div>
            <label htmlFor="limit-input">Limit:</label>
            <input
              id="limit-input"
              type="number"
              min="1"
              max="1000"
              value={limit}
              onChange={(e) => {
                setLimit(parseInt(e.target.value) || 50);
                setOffset(0);
              }}
              disabled={loading || !selectedCollection}
            />
          </div>
          <div>
            <label htmlFor="offset-input">Offset:</label>
            <input
              id="offset-input"
              type="number"
              min="0"
              value={offset}
              onChange={(e) => setOffset(parseInt(e.target.value) || 0)}
              disabled={loading || !selectedCollection}
            />
          </div>
          <button
            className="refresh-button"
            onClick={handleRefresh}
            disabled={loading || !selectedCollection}
          >
            {loading ? 'Loading...' : 'Refresh'}
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      {selectedCollection && (
        <div className="results-info">
          <p>
            Showing {results.length} of {totalCount} documents
            {offset > 0 && ` (starting at offset ${offset})`}
          </p>
        </div>
      )}

      {loading && (
        <div className="loading-message">
          <strong>Loading...</strong>
        </div>
      )}

      {!loading && results.length > 0 && (
        <div className="results-table-container">
          <table className="results-table">
            <thead>
              <tr>
                <th style={{ width: '50px' }}></th>
                <th>Key</th>
                <th>Data Preview</th>
                <th>Stored At</th>
              </tr>
            </thead>
            <tbody>
              {results.map((item, idx) => {
                const isExpanded = expandedRows.has(idx);
                const itemData = item.data || item;
                const storedAt = item.stored_at || item.updated_at || 'N/A';
                
                return (
                  <React.Fragment key={idx}>
                    <tr>
                      <td>
                        <button
                          className="expand-button"
                          onClick={() => toggleRowExpansion(idx)}
                        >
                          {isExpanded ? '−' : '+'}
                        </button>
                      </td>
                      <td className="key-cell">{item.key || 'N/A'}</td>
                      <td className="preview-cell">
                        {typeof itemData === 'object'
                          ? JSON.stringify(itemData).substring(0, 100) + '...'
                          : String(itemData).substring(0, 100)}
                      </td>
                      <td>{new Date(storedAt).toLocaleString()}</td>
                    </tr>
                    {isExpanded && (
                      <tr className="expanded-row">
                        <td colSpan="4">
                          <div className="expanded-content">
                            <h4>Full Document:</h4>
                            <pre>{JSON.stringify(item, null, 2)}</pre>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {!loading && selectedCollection && results.length === 0 && !error && (
        <div className="no-results">
          <p>No documents found in collection "{selectedCollection}"</p>
        </div>
      )}

      {selectedCollection && results.length > 0 && (
        <div className="pagination-controls">
          <button
            onClick={() => setOffset(Math.max(0, offset - limit))}
            disabled={offset === 0 || loading}
          >
            Previous
          </button>
          <span>
            Page {Math.floor(offset / limit) + 1} (offset {offset})
          </span>
          <button
            onClick={() => setOffset(offset + limit)}
            disabled={offset + limit >= totalCount || loading}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}

export default CollectionExplorer;

