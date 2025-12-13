const express = require('express');
const path = require('path');
const { createProxyMiddleware } = require('http-proxy-middleware');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3001;
const API_URL = process.env.API_URL || 'http://localhost:8007';

// Middleware
app.use(cors());
app.use(express.json());

// Serve static files from React build
app.use(express.static(path.join(__dirname, 'client/build')));

// Proxy API requests to FastAPI backend
app.use('/api', createProxyMiddleware({
    target: API_URL,
    changeOrigin: true,
    pathRewrite: {
        '^/api': '',  // Remove /api prefix when forwarding
    },
    onProxyReq: (proxyReq, req, res) => {
        console.log(`[Proxy] ${req.method} ${req.url} -> ${API_URL}${req.url.replace('/api', '')}`);
    },
    onError: (err, req, res) => {
        console.error('[Proxy Error]', err.message);
        res.status(500).json({ error: 'Proxy error', message: err.message });
    }
}));

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'ok', service: 'stock-miniapp-web' });
});

// Serve React app for all other routes
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'client/build', 'index.html'));
});

app.listen(PORT, () => {
    console.log(`🚀 Stock Mini-App Web Server running on http://localhost:${PORT}`);
    console.log(`📡 Proxying API requests to: ${API_URL}`);
});

