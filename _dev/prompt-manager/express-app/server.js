/**
 * Express server that calls PromptManager FastAPI service
 * 
 * Runs on port 3000
 * Calls FastAPI service on port 8000
 */

const express = require('express');
const axios = require('axios');
const cors = require('cors');

const app = express();
const PORT = 3000;
// Use 127.0.0.1 instead of localhost to avoid IPv6 issues
const FASTAPI_URL = process.env.FASTAPI_URL || 'http://127.0.0.1:8000';

// Middleware
app.use(cors());
app.use(express.json());

// Health check
app.get('/health', async (req, res) => {
  try {
    // Check FastAPI service health
    const response = await axios.get(`${FASTAPI_URL}/health`);
    res.json({
      status: 'healthy',
      express: 'running',
      fastapi: response.data
    });
  } catch (error) {
    res.status(503).json({
      status: 'unhealthy',
      express: 'running',
      fastapi: 'unavailable',
      error: error.message
    });
  }
});

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    service: 'Trainer Express App',
    version: '0.1.0',
    description: 'Main application that calls PromptManager microservice',
    endpoints: {
      health: '/health',
      stats: '/api/stats',
      prompt: {
        load: 'POST /api/prompt/load',
        loadContexts: 'POST /api/prompt/load-contexts',
        fill: 'POST /api/prompt/fill',
        compose: 'POST /api/prompt/compose'
      }
    },
    fastapi_service: FASTAPI_URL
  });
});

// Proxy to FastAPI stats endpoint
app.get('/api/stats', async (req, res) => {
  try {
    const response = await axios.get(`${FASTAPI_URL}/stats`);
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: error.message,
      details: error.response?.data
    });
  }
});

// Load prompt endpoint
app.post('/api/prompt/load', async (req, res) => {
  try {
    const response = await axios.post(`${FASTAPI_URL}/prompt/load`, req.body);
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: error.message,
      details: error.response?.data
    });
  }
});

// Load contexts endpoint
app.post('/api/prompt/load-contexts', async (req, res) => {
  try {
    const response = await axios.post(`${FASTAPI_URL}/prompt/load-contexts`, req.body);
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: error.message,
      details: error.response?.data
    });
  }
});

// Fill template endpoint
app.post('/api/prompt/fill', async (req, res) => {
  try {
    const response = await axios.post(`${FASTAPI_URL}/prompt/fill`, req.body);
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: error.message,
      details: error.response?.data
    });
  }
});

// Compose prompts endpoint
app.post('/api/prompt/compose', async (req, res) => {
  try {
    const response = await axios.post(`${FASTAPI_URL}/prompt/compose`, req.body);
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: error.message,
      details: error.response?.data
    });
  }
});

// Test endpoint
app.post('/api/prompt/test', async (req, res) => {
  try {
    const response = await axios.post(`${FASTAPI_URL}/prompt/test`);
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: error.message,
      details: error.response?.data
    });
  }
});

// Export app for testing
module.exports = app;

// Start server only if not in test environment
if (require.main === module) {
  app.listen(PORT, () => {
    console.log('='.repeat(80));
    console.log('Trainer Express App');
    console.log('='.repeat(80));
    console.log();
    console.log(`Server running on http://localhost:${PORT}`);
    console.log();
    console.log('Endpoints:');
    console.log(`  - http://localhost:${PORT}/              - API info`);
    console.log(`  - http://localhost:${PORT}/health         - Health check`);
    console.log(`  - http://localhost:${PORT}/api/stats      - Token stats`);
    console.log(`  - http://localhost:${PORT}/api/prompt/*    - Prompt operations`);
    console.log();
    console.log('FastAPI Service:', FASTAPI_URL);
    console.log();
    console.log('Next steps:');
    console.log('  1. Make sure FastAPI service is running on port 8000');
    console.log('  2. Test endpoints via browser or curl');
    console.log('  3. View API docs: http://localhost:8000/docs');
    console.log();
    console.log('='.repeat(80));
  });
}

