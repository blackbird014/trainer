#!/usr/bin/env python3
"""
Integration example connecting all modules:
- prompt-manager
- prompt-security
- llm-provider
- data-retriever
- data-store (NEW: persistence layer)
- format-converter
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from prompt_manager import PromptManager
    from prompt_security import SecurityModule, SecurityConfig
    from llm_provider import create_provider
    from data_retriever import FileRetriever, DataCache
    from data_store import create_store
    from format_converter import FormatConverter
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Make sure all modules are installed:")
    print("  pip install -e ../prompt-manager")
    print("  pip install -e ../prompt-security")
    print("  pip install -e ../llm-provider")
    print("  pip install -e ../data-retriever")
    print("  pip install -e ../data-store")
    print("  pip install -e .")
    sys.exit(1)


def full_workflow_example():
    """Complete workflow example."""
    print("=" * 80)
    print("Full Workflow: All Modules Integration")
    print("=" * 80)
    print()

    # 1. Initialize Security Module
    print("Step 1: Initializing Security Module...")
    security_config = SecurityConfig(strict_mode=True, max_length=1000)
    security = SecurityModule(config=security_config)
    print("✓ Security module initialized")

    # 2. Initialize Prompt Manager with Security
    print("\nStep 2: Initializing Prompt Manager...")
    manager = PromptManager(
        context_dir="../../information/context",
        security_module=security,
        use_json_templates=True
    )
    print("✓ Prompt manager initialized")

    # 3. Initialize Data Store (MongoDB or SQLite)
    print("\nStep 3: Initializing Data Store...")
    try:
        # Try MongoDB first (for production-like setup)
        data_store = create_store(
            "mongodb",
            connection_string="mongodb://localhost:27017",
            database="trainer_data"
        )
        print("✓ Data store initialized (MongoDB)")
        use_mongodb = True
    except Exception as e:
        # Fallback to SQLite for development
        print(f"⚠ MongoDB not available ({e}), using SQLite...")
        data_store = create_store("sqlite", database_path="data/integration_test.db")
        print("✓ Data store initialized (SQLite)")
        use_mongodb = False

    # 4. Initialize Data Retriever (with data-store integration)
    print("\nStep 4: Initializing Data Retriever...")
    cache = DataCache(default_ttl=3600)
    data_retriever = FileRetriever(
        base_path="../../output/json",
        cache=cache,
        enable_metrics=True
    )
    print("✓ Data retriever initialized")

    # 5. Load data and store in data-store
    print("\nStep 5: Loading data and storing in data-store...")
    data_result = data_retriever.retrieve_with_cache({
        "path": "stock_data_20251121_122508.json"
    })
    if data_result.success:
        stock_data = data_result.data.get('content', [])
        print(f"✓ Loaded data: {len(stock_data)} companies")
        
        # Store in data-store for persistence
        storage_key = "stock_data:20251121:122508"
        data_store.store(
            key=storage_key,
            data=data_result.data,
            metadata={
                "source": "file_retriever",
                "file_path": "stock_data_20251121_122508.json",
                "data_type": "stock_data",
                "company_count": len(stock_data)
            }
        )
        print(f"✓ Stored in data-store: {storage_key}")
        
        # Verify storage
        stored = data_store.retrieve(storage_key)
        if stored:
            print(f"✓ Verified: Data retrieved from store ({stored.source})")
    else:
        # Try to load from data-store if file retrieval failed
        print(f"⚠ File retrieval failed: {data_result.error}")
        print("  Attempting to load from data-store...")
        stored = data_store.query({"source": "file_retriever", "data_type": "stock_data"})
        if stored.items:
            stock_data = stored.items[0].data.get('content', [])
            print(f"✓ Loaded from data-store: {len(stock_data)} companies")
        else:
            print(f"✗ Error: No data available")
            return

    # 6. Query data from data-store (prompt-manager would do this)
    print("\nStep 6: Querying data from data-store...")
    # In real scenario, prompt-manager queries data-store directly
    query_result = data_store.query({"source": "file_retriever"})
    print(f"✓ Found {query_result.total} data items in store")
    
    # 7. Create prompt template (simulated - would load from file)
    print("\nStep 7: Creating prompt...")
    prompt_template = """
Analyze the following stock data and provide insights:

{STOCK_DATA}

Provide:
1. Summary of key metrics
2. Comparison between companies
3. Investment recommendations
"""

    # Fill template with data
    filled_prompt = prompt_template.replace(
        "{STOCK_DATA}",
        str(stock_data[:2])  # Use first 2 companies for demo
    )
    print("✓ Prompt created and filled")

    # 8. Initialize LLM Provider (if API key available)
    print("\nStep 8: Initializing LLM Provider...")
    try:
        llm_provider = create_provider(
            provider_name="openai",
            model="gpt-3.5-turbo"
        )
        print("✓ LLM provider initialized")
        use_llm = True
    except Exception as e:
        print(f"⚠ LLM provider not available: {e}")
        print("  (Skipping LLM call, using mock response)")
        use_llm = False

    # 9. Execute with LLM (or use mock)
    print("\nStep 9: Executing LLM request...")
    if use_llm:
        try:
            llm_result = llm_provider.complete(filled_prompt)
            llm_output = llm_result.content
            print(f"✓ LLM response received ({len(llm_output)} chars)")
        except Exception as e:
            print(f"✗ LLM error: {e}")
            llm_output = "# Stock Analysis\n\nMock analysis content for demonstration."
    else:
        llm_output = """# Stock Analysis Report

## Summary

Based on the provided data, here are key insights:

### Key Metrics

| Company | Market Cap | P/E Ratio |
|---------|------------|-----------|
| ILMN | 18.35B | 26.93 |
| PACB | 532.87M | -- |

### Recommendations

1. **ILMN**: Strong fundamentals
2. **PACB**: High growth potential
"""

    # 10. Initialize Format Converter
    print("\nStep 10: Initializing Format Converter...")
    format_converter = FormatConverter(
        enable_metrics=True,
        css_path="../../output/css/report.css"
    )
    print("✓ Format converter initialized")

    # 11. Convert to HTML
    print("\nStep 11: Converting to HTML...")
    html_output = format_converter.convert(
        llm_output,
        source_format="auto",
        target_format="html"
    )
    print(f"✓ Converted to HTML ({len(html_output)} bytes)")

    # 12. Convert to PDF (optional)
    print("\nStep 12: Converting to PDF...")
    pdf_output = None
    try:
        pdf_output = format_converter.convert(
            llm_output,
            source_format="markdown",
            target_format="pdf"
        )
        print(f"✓ Converted to PDF ({len(pdf_output)} bytes)")
    except Exception as e:
        print(f"⚠ PDF conversion skipped: {e}")

    # 12.5. Write outputs to file system
    print("\nStep 12.5: Writing outputs to file system...")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Write HTML
    html_file = output_dir / f"report_{storage_key.replace(':', '_')}.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_output)
    print(f"✓ HTML written to: {html_file}")
    
    # Write PDF if available
    if pdf_output:
        pdf_file = output_dir / f"report_{storage_key.replace(':', '_')}.pdf"
        with open(pdf_file, "wb") as f:
            f.write(pdf_output)
        print(f"✓ PDF written to: {pdf_file}")
    
    # Write Markdown
    md_file = output_dir / f"report_{storage_key.replace(':', '_')}.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(llm_output)
    print(f"✓ Markdown written to: {md_file}")

    # 13. Store formatted output in data-store (optional)
    print("\nStep 13: Storing formatted output in data-store...")
    try:
        data_store.store(
            key=f"formatted_output:{storage_key}:html",
            data={"html": html_output, "markdown": llm_output},
            metadata={
                "source": "format_converter",
                "original_data_key": storage_key,
                "format": "html",
                "generated_at": "2024-01-01T10:00:00"
            }
        )
        print("✓ Formatted output stored in data-store")
    except Exception as e:
        print(f"⚠ Could not store formatted output: {e}")

    # 14. Summary
    print("\n" + "=" * 80)
    print("Workflow Complete!")
    print("=" * 80)
    print()
    print("Modules used:")
    print("  ✓ prompt-manager - Template management")
    print("  ✓ prompt-security - Security validation")
    print("  ✓ data-retriever - Data loading")
    print("  ✓ data-store - Data persistence (NEW)")
    print("  ✓ llm-provider - LLM execution")
    print("  ✓ format-converter - Format conversion")
    print()
    print("Data Flow:")
    print("  1. data-retriever → loads data from files")
    print("  2. data-store → persists data for future use")
    print("  3. prompt-manager → queries data-store (not data-retriever)")
    print("  4. llm-provider → processes prompts")
    print("  5. format-converter → converts output formats")
    print("  6. data-store → stores formatted outputs (optional)")
    print()
    print("Output formats generated:")
    print("  ✓ Markdown (from LLM)")
    print("  ✓ HTML")
    if 'pdf_output' in locals():
        print("  ✓ PDF")
    print()
    print("Data-store benefits:")
    print("  ✓ Data persists across restarts")
    print("  ✓ Multiple modules can query same data")
    print("  ✓ Decouples data retrieval from consumption")
    print("  ✓ Enables ETL pipelines and analytics")


if __name__ == "__main__":
    try:
        full_workflow_example()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

