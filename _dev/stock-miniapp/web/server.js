const express = require('express');
const path = require('path');
const cors = require('cors');
const http = require('http');

const app = express();
const PORT = process.env.PORT || 3003;  // Changed from 3001 to avoid conflict with Grafana
const DATA_STORE_URL = process.env.DATA_STORE_URL || 'http://127.0.0.1:8007';
const DATA_RETRIEVER_URL = process.env.DATA_RETRIEVER_URL || 'http://127.0.0.1:8003';
const ORCHESTRATOR_URL = process.env.ORCHESTRATOR_URL || 'http://127.0.0.1:3002';

// Middleware
app.use(cors());
app.use(express.json());

// Proxy for /monitoring/* routes (to orchestrator)
app.use('/monitoring', (req, res) => {
    const targetPath = '/monitoring' + req.url;  // Add back /monitoring prefix (Express strips it)
    const targetPort = 3002;
    
    console.log(`[Proxy] ${req.method} ${req.url} -> ${ORCHESTRATOR_URL}${targetPath}`);
    
    const body = req.body ? JSON.stringify(req.body) : '';
    
    const options = {
        hostname: '127.0.0.1',
        port: targetPort,
        path: targetPath,
        method: req.method,
        headers: {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(body)
        }
    };
    
    const proxyReq = http.request(options, (proxyRes) => {
        console.log(`[Proxy] Response: ${proxyRes.statusCode} for ${req.url}`);
        
        res.status(proxyRes.statusCode);
        
        Object.keys(proxyRes.headers).forEach(key => {
            if (!['connection', 'transfer-encoding'].includes(key.toLowerCase())) {
                res.setHeader(key, proxyRes.headers[key]);
            }
        });
        
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
    
    proxyReq.setTimeout(120000, () => {
        console.error('[Proxy] Timeout for', req.url);
        proxyReq.destroy();
        if (!res.headersSent) {
            res.status(504).json({ error: 'Gateway timeout' });
        }
    });
    
    if (body) {
        proxyReq.write(body);
    }
    proxyReq.end();
});

// Manual proxy for API requests (bypassing http-proxy-middleware issues)
// IMPORTANT: This must be BEFORE static file serving to catch /api routes
app.use('/api', (req, res) => {
    const targetPath = req.url.replace('/api', '');
    
    // Route to orchestrator for /prompt/* endpoints
    if (targetPath.startsWith('/prompt/')) {
        const targetUrl = `${ORCHESTRATOR_URL}${targetPath}`;
        const targetPort = 3002;
        
        console.log(`[Proxy] ${req.method} ${req.url} -> ${targetUrl}`);
        
        const body = req.body ? JSON.stringify(req.body) : '';
        
        const options = {
            hostname: '127.0.0.1',
            port: targetPort,
            path: targetPath,
            method: req.method,
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(body)
            }
        };
        
        const proxyReq = http.request(options, (proxyRes) => {
            console.log(`[Proxy] Response: ${proxyRes.statusCode} for ${req.url}`);
            
            res.status(proxyRes.statusCode);
            
            Object.keys(proxyRes.headers).forEach(key => {
                if (!['connection', 'transfer-encoding'].includes(key.toLowerCase())) {
                    res.setHeader(key, proxyRes.headers[key]);
                }
            });
            
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
        
        proxyReq.setTimeout(120000, () => {
            console.error('[Proxy] Timeout for', req.url);
            proxyReq.destroy();
            if (!res.headersSent) {
                res.status(504).json({ error: 'Gateway timeout' });
            }
        });
        
        if (body) {
            proxyReq.write(body);
        }
        proxyReq.end();
        return;
    }
    
    // Route to data-retriever for /retrieve endpoint, otherwise data-store
    const isRetrieve = targetPath === '/retrieve' || targetPath.startsWith('/retrieve');
    const targetUrl = isRetrieve ? `${DATA_RETRIEVER_URL}${targetPath}` : `${DATA_STORE_URL}${targetPath}`;
    const targetPort = isRetrieve ? 8003 : 8007;
    
    console.log(`[Proxy] ${req.method} ${req.url} -> ${targetUrl}`);
    
    // Get body (Express already parsed it, but we need to stringify for forwarding)
    const body = req.body ? JSON.stringify(req.body) : '';
    
    const options = {
        hostname: '127.0.0.1',
        port: targetPort,
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

// Serve static files from React build (AFTER API routes)
app.use(express.static(path.join(__dirname, 'client/build')));

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
    console.log(`📡 Proxying data-store requests to: ${DATA_STORE_URL}`);
    console.log(`📡 Proxying data-retriever requests to: ${DATA_RETRIEVER_URL}`);
    console.log(`📡 Proxying orchestrator requests to: ${ORCHESTRATOR_URL}`);
});

