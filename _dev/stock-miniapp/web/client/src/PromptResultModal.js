import React, { useState, useEffect } from 'react';
import './PromptResultModal.css';

function PromptResultModal({ isOpen, onClose, runId, ticker }) {
  const [activeTab, setActiveTab] = useState('html');
  const [loading, setLoading] = useState(true);
  const [content, setContent] = useState({ html: '', md: '', json: null });
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen && runId) {
      loadContent();
    }
  }, [isOpen, runId]);

  const loadContent = async () => {
    setLoading(true);
    setError(null);

    try {
      // Load HTML by default
      const response = await fetch(`/api/prompt/run/${runId}/html`);
      if (response.ok) {
        const html = await response.text();
        setContent(prev => ({ ...prev, html }));
      } else {
        throw new Error('Failed to load HTML');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadTabContent = async (tab) => {
    if (content[tab]) {
      return; // Already loaded
    }

    setLoading(true);
    try {
      let url = '';
      if (tab === 'md') {
        url = `/api/prompt/run/${runId}/md`;
      } else if (tab === 'json') {
        url = `/api/prompt/run/${runId}/json`;
      }

      if (url) {
        const response = await fetch(url);
        if (response.ok) {
          if (tab === 'json') {
            const json = await response.json();
            setContent(prev => ({ ...prev, json }));
          } else {
            const text = await response.text();
            setContent(prev => ({ ...prev, [tab]: text }));
          }
        }
      }
    } catch (err) {
      console.error(`Error loading ${tab}:`, err);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    loadTabContent(tab);
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Analysis Result: {ticker}</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <div className="modal-tabs">
          <button
            className={activeTab === 'html' ? 'active' : ''}
            onClick={() => handleTabChange('html')}
          >
            HTML
          </button>
          <button
            className={activeTab === 'md' ? 'active' : ''}
            onClick={() => handleTabChange('md')}
          >
            Markdown
          </button>
          <button
            className={activeTab === 'json' ? 'active' : ''}
            onClick={() => handleTabChange('json')}
          >
            JSON
          </button>
        </div>

        <div className="modal-body">
          {loading && !content[activeTab] && (
            <div className="loading">Loading...</div>
          )}

          {error && (
            <div className="error">Error: {error}</div>
          )}

          {!loading && !error && (
            <>
              {activeTab === 'html' && content.html && (
                <div
                  className="html-content"
                  dangerouslySetInnerHTML={{ __html: content.html }}
                />
              )}

              {activeTab === 'md' && content.md && (
                <pre className="md-content">{content.md}</pre>
              )}

              {activeTab === 'json' && content.json && (
                <pre className="json-content">
                  {JSON.stringify(content.json, null, 2)}
                </pre>
              )}

              {!content.html && !content.md && !content.json && (
                <div className="error">No content available. The prompt flow may have failed.</div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default PromptResultModal;

