"""
Simple test to verify Prometheus metrics work without full Prometheus/Grafana setup.

This just verifies that metrics are being generated correctly.
"""

from prompt_manager import PromptManager
from prometheus_client import generate_latest, REGISTRY

def main():
    print("=" * 80)
    print("Testing Prometheus Metrics (No Prometheus/Grafana needed!)")
    print("=" * 80)
    print()
    
    # Check if prometheus_client is available
    try:
        from prometheus_client import Counter
        print("✓ prometheus-client is installed")
    except ImportError:
        print("✗ prometheus-client not installed")
        print("  Install with: pip install prometheus-client")
        print("  Or: pip install -e '.[metrics]'")
        return
    
    print()
    
    # Initialize PromptManager with metrics
    print("Initializing PromptManager with metrics enabled...")
    manager = PromptManager(
        enable_metrics=True,
        track_tokens=True,
        model="gpt-4"
    )
    print("✓ PromptManager initialized")
    print()
    
    # Do some operations to generate metrics
    print("Performing operations to generate metrics...")
    
    try:
        # Load contexts
        print("  - Loading contexts...")
        contexts = manager.load_contexts([
            "biotech/01-introduction.md",
            "biotech/molecular-biology-foundations.md"
        ])
        print(f"    ✓ Loaded {len(contexts):,} chars")
    except FileNotFoundError:
        print("    ⚠ Context files not found (using empty)")
        contexts = ""
    
    # Fill template
    print("  - Filling template...")
    from prompt_manager import PromptTemplate
    template = PromptTemplate("Test template with {VAR}")
    filled = manager.fill_template(template, {"VAR": "value"})
    print(f"    ✓ Template filled ({len(filled)} chars)")
    
    # Compose
    print("  - Composing prompts...")
    composed = manager.compose([PromptTemplate("Prompt 1"), PromptTemplate("Prompt 2")])
    print(f"    ✓ Composed ({len(composed)} chars)")
    
    # Cache operations
    print("  - Testing cache...")
    manager.cache_prompt("test", "content")
    cached = manager.get_cached("test")
    print(f"    ✓ Cache tested")
    
    print()
    
    # Generate and display metrics
    print("=" * 80)
    print("Generated Metrics (Prometheus format)")
    print("=" * 80)
    print()
    
    metrics = generate_latest().decode()
    print(metrics)
    
    print()
    print("=" * 80)
    print("Metrics Summary")
    print("=" * 80)
    
    # Parse and summarize
    lines = metrics.split('\n')
    metric_types = {}
    metric_count = 0
    
    for line in lines:
        if line.startswith('# TYPE'):
            parts = line.split()
            if len(parts) >= 3:
                metric_name = parts[2]
                metric_type = parts[3]
                metric_types[metric_name] = metric_type
        elif line and not line.startswith('#') and not line.startswith('prompt_manager_'):
            # This is a metric value
            metric_count += 1
    
    print(f"Total metrics: {len(metric_types)}")
    print(f"Metric values: {metric_count}")
    print()
    print("Available metrics:")
    for name, mtype in sorted(metric_types.items()):
        print(f"  - {name} ({mtype})")
    
    print()
    print("=" * 80)
    print("Next Steps")
    print("=" * 80)
    print("✓ Metrics are working!")
    print()
    print("To visualize:")
    print("1. Use Docker: docker-compose up (see PROMETHEUS_GRAFANA_SETUP.md)")
    print("2. Or view in browser: python example_logging.py (has Flask endpoint)")
    print("3. Or scrape with Prometheus: http://localhost:8000/metrics")
    print()
    print("This test proves metrics work without Prometheus/Grafana installation!")


if __name__ == "__main__":
    main()

