"""
Example: Logging System Usage

Demonstrates structured logging with file output, metrics, and Prometheus integration.
"""

import json
from pathlib import Path
from prompt_manager import (
    PromptManager, 
    setup_logger, 
    LogLevel,
    PromptManagerLogger
)

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


def main():
    print("=" * 80)
    print("Logging System Example")
    print("=" * 80)
    print()
    
    # Example 1: Basic logging with file output
    print("Example 1: Basic logging with JSON file output")
    print("-" * 80)
    
    log_file = PROJECT_ROOT / "_dev" / "phase1" / "prompt-manager" / "logs" / "prompt_manager.log"
    
    logger = setup_logger(
        name="prompt_manager_example",
        log_file=str(log_file),
        log_level=LogLevel.INFO,
        enable_console=True,
        enable_json=True,
        enable_metrics=True
    )
    
    logger.info("Starting PromptManager example")
    logger.info("Logger configured", log_file=str(log_file))
    print()
    
    # Example 2: PromptManager with logging
    print("Example 2: PromptManager with integrated logging")
    print("-" * 80)
    
    manager = PromptManager(
        context_dir=str(PROJECT_ROOT / "information" / "context"),
        cache_enabled=True,
        track_tokens=True,
        model="gpt-4",
        log_file=str(log_file),
        log_level=LogLevel.INFO,
        enable_metrics=True
    )
    
    # Operations will be automatically logged
    print("Loading contexts (will be logged automatically)...")
    try:
        contexts = manager.load_contexts([
            "biotech/01-introduction.md",
            "biotech/molecular-biology-foundations.md"
        ])
        print(f"✓ Loaded contexts ({len(contexts):,} chars)")
    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
        contexts = ""
    
    print()
    
    # Example 3: Custom logging messages
    print("Example 3: Custom logging with context")
    print("-" * 80)
    
    manager.logger.info(
        "Custom log message with context",
        operation="custom_operation",
        duration=0.123,
        tokens=1000,
        cost=0.03,
        custom_field="custom_value"
    )
    
    print()
    
    # Example 4: Error logging
    print("Example 4: Error logging")
    print("-" * 80)
    
    try:
        # This will fail and be logged
        manager.load_contexts(["nonexistent_file.md"])
    except FileNotFoundError:
        # Error is automatically logged by PromptManager
        pass
    
    print()
    
    # Example 5: Cache logging
    print("Example 5: Cache hit/miss logging")
    print("-" * 80)
    
    # Cache miss
    cached = manager.get_cached("test_prompt")
    print("Cache miss logged")
    
    # Cache hit (after caching)
    manager.cache_prompt("test_prompt", "test content")
    cached = manager.get_cached("test_prompt")
    print("Cache hit logged")
    
    print()
    
    # Example 6: View log file
    print("Example 6: View log file contents")
    print("-" * 80)
    
    if log_file.exists():
        print(f"Log file: {log_file}")
        print(f"Size: {log_file.stat().st_size} bytes")
        print()
        print("Last 5 log entries (JSON format):")
        print("-" * 80)
        
        with open(log_file, 'r') as f:
            lines = f.readlines()
            for line in lines[-5:]:
                try:
                    log_entry = json.loads(line.strip())
                    print(f"  [{log_entry.get('level')}] {log_entry.get('message')}")
                    if 'operation' in log_entry:
                        print(f"    Operation: {log_entry['operation']}")
                    if 'duration' in log_entry:
                        print(f"    Duration: {log_entry['duration']:.3f}s")
                    if 'tokens' in log_entry:
                        print(f"    Tokens: {log_entry['tokens']:,}")
                    print()
                except json.JSONDecodeError:
                    print(f"  {line.strip()}")
    else:
        print("Log file not created yet")
    
    print()
    
    # Example 7: Prometheus metrics endpoint (if available)
    print("Example 7: Prometheus metrics")
    print("-" * 80)
    
    metrics_handler = manager.logger.get_metrics_endpoint()
    if metrics_handler:
        print("✓ Prometheus metrics endpoint available")
        print("  You can expose this via Flask/FastAPI:")
        print("  @app.route('/metrics')")
        print("  def metrics():")
        print("      return metrics_handler()")
        print()
        print("  Then scrape with Prometheus and visualize in Grafana!")
    else:
        print("✗ Prometheus client not installed")
        print("  Install with: pip install prometheus-client")
        print("  Or: pip install -e '.[metrics]'")
    
    print()
    
    # Summary
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print("✓ Structured JSON logging enabled")
    print("✓ File logging configured")
    print("✓ Prometheus metrics integrated")
    print("✓ Automatic operation tracking")
    print("✓ Cache hit/miss tracking")
    print()
    print("Log file location:", log_file)
    print()
    print("Next steps:")
    print("1. Review log file for structured JSON logs")
    print("2. Set up Prometheus to scrape metrics endpoint")
    print("3. Create Grafana dashboards for visualization")
    print("4. Configure database logging if needed")


if __name__ == "__main__":
    main()

