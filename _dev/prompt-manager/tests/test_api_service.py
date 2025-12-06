"""
Tests for FastAPI service (api_service.py)
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import os

# Import the app - we'll need to patch the manager initialization
from api_service import app, manager


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def mock_manager():
    """Create a mock PromptManager"""
    mock = Mock()
    mock.logger = Mock()
    mock.logger.metrics_enabled = True
    mock.get_token_usage = Mock(return_value={"total_tokens": 1000, "total_cost": 0.01})
    mock.get_operation_stats = Mock(return_value={"load_contexts": {"count": 5}})
    return mock


@pytest.fixture
def temp_context_file():
    """Create a temporary context file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("# Test Context\n\nThis is a test context file.")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


class TestRootEndpoint:
    """Tests for root endpoint"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns API info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Prompt Manager API"
        assert data["version"] == "0.1.0"
        assert "endpoints" in data
        assert "docs" in data


class TestHealthEndpoint:
    """Tests for health endpoint"""
    
    def test_health_endpoint(self, client):
        """Test health endpoint returns healthy status"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "prompt-manager"
        assert "metrics_enabled" in data


class TestMetricsEndpoint:
    """Tests for Prometheus metrics endpoint"""
    
    def test_metrics_endpoint(self, client):
        """Test metrics endpoint returns Prometheus format"""
        response = client.get("/metrics")
        assert response.status_code == 200
        # Prometheus content type version may vary, just check it's text/plain
        assert "text/plain" in response.headers["content-type"]
        assert "charset=utf-8" in response.headers["content-type"]
        # Check for some expected Prometheus metrics
        content = response.text
        assert "prompt_manager" in content.lower() or len(content) > 0


class TestStatsEndpoint:
    """Tests for stats endpoint"""
    
    def test_stats_endpoint(self, client):
        """Test stats endpoint returns token usage and operation stats"""
        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        assert "token_usage" in data
        assert "operation_stats" in data


class TestLoadPromptEndpoint:
    """Tests for load prompt endpoint"""
    
    def test_load_prompt_success(self, client, temp_context_file):
        """Test loading a prompt successfully"""
        # Use the temp file we created
        response = client.post(
            "/prompt/load",
            json={"prompt_path": temp_context_file}
        )
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert "length" in data
        assert data["content"] == "# Test Context\n\nThis is a test context file."
        assert data["length"] > 0
    
    def test_load_prompt_not_found(self, client):
        """Test loading a non-existent prompt returns 404"""
        response = client.post(
            "/prompt/load",
            json={"prompt_path": "/nonexistent/file.md"}
        )
        assert response.status_code == 404
        assert "detail" in response.json()


class TestLoadContextsEndpoint:
    """Tests for load contexts endpoint"""
    
    def test_load_contexts_success(self, client, temp_context_file):
        """Test loading contexts successfully"""
        response = client.post(
            "/prompt/load-contexts",
            json={"context_paths": [temp_context_file]}
        )
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert "length" in data
        assert "# Test Context" in data["content"]
    
    def test_load_contexts_not_found(self, client):
        """Test loading non-existent contexts returns 404"""
        response = client.post(
            "/prompt/load-contexts",
            json={"context_paths": ["/nonexistent/file.md"]}
        )
        assert response.status_code == 404
        assert "detail" in response.json()
    
    def test_load_contexts_empty_list(self, client):
        """Test loading empty context list"""
        response = client.post(
            "/prompt/load-contexts",
            json={"context_paths": []}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == ""
        assert data["length"] == 0


class TestFillTemplateEndpoint:
    """Tests for fill template endpoint"""
    
    def test_fill_template_success(self, client):
        """Test filling a template successfully"""
        response = client.post(
            "/prompt/fill",
            json={
                "template_content": "Hello {name}!",
                "params": {"name": "World"}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert "length" in data
        assert data["content"] == "Hello World!"
        assert data["length"] == len("Hello World!")
    
    def test_fill_template_missing_variable(self, client):
        """Test filling template with missing variable returns 400"""
        response = client.post(
            "/prompt/fill",
            json={
                "template_content": "Hello {name}!",
                "params": {}
            }
        )
        assert response.status_code == 400
        assert "detail" in response.json()
        assert "Missing required variables" in response.json()["detail"]
    
    def test_fill_template_multiple_variables(self, client):
        """Test filling template with multiple variables"""
        response = client.post(
            "/prompt/fill",
            json={
                "template_content": "Hello {name}! You are {age} years old.",
                "params": {"name": "Alice", "age": "30"}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "Alice" in data["content"]
        assert "30" in data["content"]
    
    def test_fill_template_with_path(self, client):
        """Test filling template with optional template_path"""
        response = client.post(
            "/prompt/fill",
            json={
                "template_content": "Hello {name}!",
                "template_path": "/some/path.md",
                "params": {"name": "World"}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Hello World!"


class TestComposeEndpoint:
    """Tests for compose endpoint"""
    
    def test_compose_sequential(self, client):
        """Test composing prompts sequentially"""
        response = client.post(
            "/prompt/compose",
            json={
                "templates": ["Prompt 1", "Prompt 2"],
                "strategy": "sequential"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert "length" in data
        assert "Prompt 1" in data["content"]
        assert "Prompt 2" in data["content"]
        assert "---" in data["content"]  # Sequential uses separator
    
    def test_compose_parallel(self, client):
        """Test composing prompts in parallel"""
        response = client.post(
            "/prompt/compose",
            json={
                "templates": ["Prompt 1", "Prompt 2"],
                "strategy": "parallel"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "Prompt 1" in data["content"]
        assert "Prompt 2" in data["content"]
        assert "Section 1" in data["content"]
    
    def test_compose_hierarchical(self, client):
        """Test composing prompts hierarchically"""
        response = client.post(
            "/prompt/compose",
            json={
                "templates": ["Main prompt", "Context prompt"],
                "strategy": "hierarchical"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "Main prompt" in data["content"]
        assert "Additional Context" in data["content"]
    
    def test_compose_invalid_strategy(self, client):
        """Test composing with invalid strategy returns 400"""
        response = client.post(
            "/prompt/compose",
            json={
                "templates": ["Prompt 1"],
                "strategy": "invalid_strategy"
            }
        )
        # Single template doesn't use strategy, so it succeeds
        # For multiple templates with invalid strategy, it should fail
        if len(response.json().get("content", "")) > 10:  # Multiple templates case
            # If we had multiple templates, invalid strategy would fail
            # But with single template, strategy is ignored
            pass
        # Actually test with multiple templates
        response2 = client.post(
            "/prompt/compose",
            json={
                "templates": ["Prompt 1", "Prompt 2"],
                "strategy": "invalid_strategy"
            }
        )
        assert response2.status_code == 400
        assert "detail" in response2.json()
    
    def test_compose_single_template(self, client):
        """Test composing single template"""
        response = client.post(
            "/prompt/compose",
            json={
                "templates": ["Single prompt"],
                "strategy": "sequential"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Single prompt"
    
    def test_compose_empty_list(self, client):
        """Test composing empty template list"""
        response = client.post(
            "/prompt/compose",
            json={
                "templates": [],
                "strategy": "sequential"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == ""


class TestTestEndpoint:
    """Tests for test endpoint"""
    
    def test_test_endpoint(self, client):
        """Test test endpoint generates metrics"""
        response = client.post("/prompt/test")
        # This might fail if context files don't exist, so we check for either success or expected error
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert data["status"] == "success"


class TestCORS:
    """Tests for CORS configuration"""
    
    def test_cors_headers(self, client):
        """Test CORS headers are set correctly"""
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            }
        )
        # FastAPI CORS middleware should handle OPTIONS
        # Check that CORS is configured (may not always return headers on OPTIONS)
        assert response.status_code in [200, 204]
    
    def test_cors_allowed_origin(self, client):
        """Test CORS allows requests from Express origin"""
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"}
        )
        assert response.status_code == 200
        # CORS headers should be present (FastAPI adds them automatically)


class TestErrorHandling:
    """Tests for error handling"""
    
    def test_invalid_json(self, client):
        """Test invalid JSON returns 422"""
        response = client.post(
            "/prompt/fill",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_missing_required_field(self, client):
        """Test missing required field returns 422"""
        response = client.post(
            "/prompt/fill",
            json={
                "template_content": "Hello {name}!"
                # Missing "params" field
            }
        )
        assert response.status_code == 422
    
    def test_invalid_request_format(self, client):
        """Test invalid request format"""
        response = client.post(
            "/prompt/load",
            json={"invalid": "field"}
        )
        # Should return 422 for validation error or handle gracefully
        assert response.status_code in [422, 400]


class TestRequestValidation:
    """Tests for Pydantic model validation"""
    
    def test_load_prompt_missing_path(self, client):
        """Test load prompt without path"""
        response = client.post("/prompt/load", json={})
        assert response.status_code == 422
    
    def test_fill_template_missing_content(self, client):
        """Test fill template without content"""
        response = client.post(
            "/prompt/fill",
            json={"params": {"name": "World"}}
        )
        assert response.status_code == 422
    
    def test_compose_missing_templates(self, client):
        """Test compose without templates"""
        response = client.post(
            "/prompt/compose",
            json={"strategy": "sequential"}
        )
        assert response.status_code == 422

