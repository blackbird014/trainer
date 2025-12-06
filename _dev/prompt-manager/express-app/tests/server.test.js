/**
 * Tests for Express server (server.js)
 * 
 * Tests the proxy functionality and error handling
 */

const request = require('supertest');
const axios = require('axios');

// Mock axios before importing the server
jest.mock('axios');

// Set test environment
process.env.FASTAPI_URL = 'http://localhost:8000';

// Import server after mocking axios
const app = require('../server');

describe('Express Server', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('GET /', () => {
    test('should return API information', async () => {
      const response = await request(app).get('/');
      
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('service');
      expect(response.body).toHaveProperty('version');
      expect(response.body).toHaveProperty('endpoints');
      expect(response.body.service).toBe('Trainer Express App');
    });
  });

  describe('GET /health', () => {
    test('should return healthy when FastAPI is available', async () => {
      axios.get.mockResolvedValue({
        data: {
          status: 'healthy',
          service: 'prompt-manager',
          metrics_enabled: true
        }
      });

      const response = await request(app).get('/health');
      
      expect(response.status).toBe(200);
      expect(response.body.status).toBe('healthy');
      expect(response.body.express).toBe('running');
      expect(response.body.fastapi).toBeDefined();
      expect(axios.get).toHaveBeenCalledWith('http://localhost:8000/health');
    });

    test('should return unhealthy when FastAPI is unavailable', async () => {
      axios.get.mockRejectedValue(new Error('Connection refused'));

      const response = await request(app).get('/health');
      
      expect(response.status).toBe(503);
      expect(response.body.status).toBe('unhealthy');
      expect(response.body.express).toBe('running');
      expect(response.body.fastapi).toBe('unavailable');
    });
  });

  describe('GET /api/stats', () => {
    test('should proxy stats request to FastAPI', async () => {
      const mockStats = {
        token_usage: { total_tokens: 1000 },
        operation_stats: { load_contexts: { count: 5 } }
      };
      
      axios.get.mockResolvedValue({ data: mockStats });

      const response = await request(app).get('/api/stats');
      
      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockStats);
      expect(axios.get).toHaveBeenCalledWith('http://localhost:8000/stats');
    });

    test('should handle FastAPI errors', async () => {
      axios.get.mockRejectedValue({
        response: { status: 500, data: { error: 'Internal server error' } }
      });

      const response = await request(app).get('/api/stats');
      
      expect(response.status).toBe(500);
      expect(response.body).toBeDefined();
      expect(response.body.error || response.body.details).toBeDefined();
    });
  });

  describe('POST /api/prompt/load', () => {
    test('should proxy load prompt request to FastAPI', async () => {
      const mockResponse = {
        content: 'Hello {name}!',
        length: 12
      };
      
      axios.post.mockResolvedValue({ data: mockResponse });

      const response = await request(app)
        .post('/api/prompt/load')
        .send({ prompt_path: '/some/path.md' });
      
      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockResponse);
      expect(axios.post).toHaveBeenCalledWith(
        'http://localhost:8000/prompt/load',
        { prompt_path: '/some/path.md' }
      );
    });

    test('should handle FastAPI errors', async () => {
      axios.post.mockRejectedValue({
        response: { status: 404, data: { detail: 'File not found' } }
      });

      const response = await request(app)
        .post('/api/prompt/load')
        .send({ prompt_path: '/nonexistent.md' });
      
      expect(response.status).toBe(404);
      expect(response.body.details).toBeDefined();
    });
  });

  describe('POST /api/prompt/load-contexts', () => {
    test('should proxy load contexts request to FastAPI', async () => {
      const mockResponse = {
        content: '# Context\n\nSome context',
        length: 20
      };
      
      axios.post.mockResolvedValue({ data: mockResponse });

      const response = await request(app)
        .post('/api/prompt/load-contexts')
        .send({ context_paths: ['context1.md'] });
      
      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockResponse);
      expect(axios.post).toHaveBeenCalledWith(
        'http://localhost:8000/prompt/load-contexts',
        { context_paths: ['context1.md'] }
      );
    });
  });

  describe('POST /api/prompt/fill', () => {
    test('should proxy fill template request to FastAPI', async () => {
      const mockResponse = {
        content: 'Hello World!',
        length: 13
      };
      
      axios.post.mockResolvedValue({ data: mockResponse });

      const response = await request(app)
        .post('/api/prompt/fill')
        .send({
          template_content: 'Hello {name}!',
          params: { name: 'World' }
        });
      
      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockResponse);
      expect(axios.post).toHaveBeenCalledWith(
        'http://localhost:8000/prompt/fill',
        {
          template_content: 'Hello {name}!',
          params: { name: 'World' }
        }
      );
    });

    test('should handle validation errors', async () => {
      axios.post.mockRejectedValue({
        response: { 
          status: 400, 
          data: { detail: 'Missing required variables: name' } 
        }
      });

      const response = await request(app)
        .post('/api/prompt/fill')
        .send({
          template_content: 'Hello {name}!',
          params: {}
        });
      
      expect(response.status).toBe(400);
      expect(response.body.details).toBeDefined();
    });
  });

  describe('POST /api/prompt/compose', () => {
    test('should proxy compose request to FastAPI', async () => {
      const mockResponse = {
        content: 'Prompt 1\n\n---\n\nPrompt 2',
        length: 25
      };
      
      axios.post.mockResolvedValue({ data: mockResponse });

      const response = await request(app)
        .post('/api/prompt/compose')
        .send({
          templates: ['Prompt 1', 'Prompt 2'],
          strategy: 'sequential'
        });
      
      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockResponse);
      expect(axios.post).toHaveBeenCalledWith(
        'http://localhost:8000/prompt/compose',
        {
          templates: ['Prompt 1', 'Prompt 2'],
          strategy: 'sequential'
        }
      );
    });
  });

  describe('POST /api/prompt/test', () => {
    test('should proxy test request to FastAPI', async () => {
      const mockResponse = {
        status: 'success',
        message: 'Test operations completed'
      };
      
      axios.post.mockResolvedValue({ data: mockResponse });

      const response = await request(app).post('/api/prompt/test');
      
      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockResponse);
      expect(axios.post).toHaveBeenCalledWith('http://localhost:8000/prompt/test');
    });
  });

  describe('Error Handling', () => {
    test('should handle network errors gracefully', async () => {
      axios.get.mockRejectedValue(new Error('Network error'));

      const response = await request(app).get('/api/stats');
      
      expect(response.status).toBe(500);
      expect(response.body.error).toBe('Network error');
    });

    test('should handle errors without response object', async () => {
      axios.post.mockRejectedValue(new Error('Connection timeout'));

      const response = await request(app)
        .post('/api/prompt/fill')
        .send({ template_content: 'Test', params: {} });
      
      expect(response.status).toBe(500);
      expect(response.body.error).toBe('Connection timeout');
    });
  });

  describe('CORS', () => {
    test('should allow CORS requests', async () => {
      const response = await request(app)
        .get('/')
        .set('Origin', 'http://localhost:3000');
      
      expect(response.status).toBe(200);
      // CORS middleware should be configured
    });
  });
});

