const express = require('express');
const path = require('path');
const cors = require('cors');
const http = require('http');

const app = express();
const PORT = process.env.PORT || 3001;
const API_URL = process.env.API_URL || 'http://127.0.0.1:8007';

// Middleware
app.use(cors());
app.use(express.json());

// Serve static files from React build
app.use(express.static(path.join(__dirname, 'client/build')));

// Manual proxy for API requests (bypassing http-proxy-middleware issues)
app.use('/api', (req, res) => {
    const targetPath = req.url.replace('/api', '');
    const targetUrl = `${API_URL}${targetPath}`;
    
    console.log(`[Proxy] ${req.method} ${req.url} -> ${targetUrl}`);
    
    // Get body (Express already parsed it, but we need to stringify for forwarding)
    const body = req.body ? JSON.stringify(req.body) : '';
    
    const options = {
        hostname: '127.0.0.1',
        port: 8007,
        path: targetPath,
        method: req.method,
        headers: {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(body)
        }
    };
    
    const proxyReq = http.request(options, (proxyRes) => {
        console.log(`[Proxy] Response: ${proxyRes.statusCode} for ${req.url}`);
        
        // Forward status code
        res.status(proxyRes.statusCode);
        
        // Forward headers (except connection-related)
        Object.keys(proxyRes.headers).forEach(key => {
            if (!['connection', 'transfer-encoding'].includes(key.toLowerCase())) {
                res.setHeader(key, proxyRes.headers[key]);
            }
        });
        
        // Pipe response data
        proxyRes.on('data', (chunk) => {
            res.write(chunk);
        });
        
        proxyRes.on('end', () => {
            res.end();
            console.log(`[Proxy] Completed: ${req.url}`);
        });
    });
    
    proxyReq.on('error', (err) => {
        console.error('[Proxy Error]', err.message);
        if (!res.headersSent) {
            res.status(500).json({ 
                error: 'Proxy error', 
                message: err.message 
            });
        }
    });
    
    // Set timeout
    proxyReq.setTimeout(120000, () => {
        console.error('[Proxy] Timeout for', req.url);
        proxyReq.destroy();
        if (!res.headersSent) {
            res.status(504).json({ error: 'Gateway timeout' });
        }
    });
    
    // Send request body
    if (body) {
        proxyReq.write(body);
    }
    proxyReq.end();
});

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

