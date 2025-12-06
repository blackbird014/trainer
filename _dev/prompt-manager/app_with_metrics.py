"""
Flask app with Prometheus metrics endpoint for PromptManager.

Run this app, then Docker containers can scrape metrics from it.
"""

from flask import Flask, jsonify
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from pathlib import Path
from prompt_manager import PromptManager, LogLevel

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

app = Flask(__name__)

# Initialize PromptManager with metrics
manager = PromptManager(
    context_dir=str(PROJECT_ROOT / "information" / "context"),
    cache_enabled=True,
    track_tokens=True,
    model="gpt-4",
    enable_metrics=True,
    log_level=LogLevel.INFO
)


@app.route('/')
def index():
    """Home page with info."""
    return """
    <h1>Prompt Manager Metrics Server</h1>
    <p>Metrics endpoint: <a href="/metrics">/metrics</a></p>
    <p>Health check: <a href="/health">/health</a></p>
    <p>Stats: <a href="/stats">/stats</a></p>
    <hr>
    <h2>Usage</h2>
    <p>1. Start this server: <code>python app_with_metrics.py</code></p>
    <p>2. Start Docker: <code>docker-compose up</code></p>
    <p>3. View Grafana: <a href="http://localhost:3000">http://localhost:3000</a></p>
    <p>4. View Prometheus: <a href="http://localhost:9090">http://localhost:9090</a></p>
    """


@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint."""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "prompt-manager",
        "metrics_enabled": manager.logger.metrics_enabled
    })


@app.route('/stats')
def stats():
    """Get current stats."""
    token_usage = manager.get_token_usage()
    operation_stats = manager.get_operation_stats()
    
    return jsonify({
        "token_usage": token_usage,
        "operation_stats": operation_stats
    })


@app.route('/test')
def test():
    """Test endpoint to generate some metrics."""
    try:
        # Load contexts
        contexts = manager.load_contexts([
            "biotech/01-introduction.md",
            "biotech/molecular-biology-foundations.md"
        ])
        
        # Fill template
        from prompt_manager import PromptTemplate
        template = PromptTemplate("Test template with {VAR}")
        filled = manager.fill_template(template, {"VAR": "test_value"})
        
        # Compose
        composed = manager.compose([
            PromptTemplate("Prompt 1"),
            PromptTemplate("Prompt 2")
        ])
        
        return jsonify({
            "status": "success",
            "message": "Test operations completed",
            "contexts_size": len(contexts),
            "filled_size": len(filled),
            "composed_size": len(composed)
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == '__main__':
    print("=" * 80)
    print("Prompt Manager Metrics Server")
    print("=" * 80)
    print()
    print("Starting server on http://0.0.0.0:8000")
    print()
    print("Endpoints:")
    print("  - http://localhost:8000/          - Home page")
    print("  - http://localhost:8000/metrics   - Prometheus metrics")
    print("  - http://localhost:8000/health     - Health check")
    print("  - http://localhost:8000/stats      - Current stats")
    print("  - http://localhost:8000/test       - Generate test metrics")
    print()
    print("Next steps:")
    print("  1. Keep this server running")
    print("  2. Start Docker: docker-compose up")
    print("  3. View Grafana: http://localhost:3000 (admin/admin)")
    print("  4. View Prometheus: http://localhost:9090")
    print()
    print("=" * 80)
    print()
    
    app.run(host='0.0.0.0', port=8000, debug=False)

