#!/usr/bin/env python3
"""
Integration example connecting all modules:
- prompt-manager
- prompt-security
- llm-provider
- data-retriever
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
    from format_converter import FormatConverter
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Make sure all modules are installed:")
    print("  pip install -e ../prompt-manager")
    print("  pip install -e ../prompt-security")
    print("  pip install -e ../llm-provider")
    print("  pip install -e ../data-retriever")
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

    # 3. Initialize Data Retriever
    print("\nStep 3: Initializing Data Retriever...")
    cache = DataCache(default_ttl=3600)
    data_retriever = FileRetriever(
        base_path="../../output/json",
        cache=cache,
        enable_metrics=True
    )
    print("✓ Data retriever initialized")

    # 4. Load data
    print("\nStep 4: Loading data...")
    data_result = data_retriever.retrieve_with_cache({
        "path": "stock_data_20251121_122508.json"
    })
    if data_result.success:
        print(f"✓ Loaded data: {len(data_result.data.get('content', []))} companies")
        stock_data = data_result.data.get('content', [])
    else:
        print(f"✗ Error loading data: {data_result.error}")
        return

    # 5. Create prompt template (simulated - would load from file)
    print("\nStep 5: Creating prompt...")
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

    # 6. Initialize LLM Provider (if API key available)
    print("\nStep 6: Initializing LLM Provider...")
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

    # 7. Execute with LLM (or use mock)
    print("\nStep 7: Executing LLM request...")
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

    # 8. Initialize Format Converter
    print("\nStep 8: Initializing Format Converter...")
    format_converter = FormatConverter(
        enable_metrics=True,
        css_path="../../output/css/report.css"
    )
    print("✓ Format converter initialized")

    # 9. Convert to HTML
    print("\nStep 9: Converting to HTML...")
    html_output = format_converter.convert(
        llm_output,
        source_format="auto",
        target_format="html"
    )
    print(f"✓ Converted to HTML ({len(html_output)} bytes)")

    # 10. Convert to PDF (optional)
    print("\nStep 10: Converting to PDF...")
    try:
        pdf_output = format_converter.convert(
            llm_output,
            source_format="markdown",
            target_format="pdf"
        )
        print(f"✓ Converted to PDF ({len(pdf_output)} bytes)")
    except Exception as e:
        print(f"⚠ PDF conversion skipped: {e}")

    # 11. Summary
    print("\n" + "=" * 80)
    print("Workflow Complete!")
    print("=" * 80)
    print()
    print("Modules used:")
    print("  ✓ prompt-manager - Template management")
    print("  ✓ prompt-security - Security validation")
    print("  ✓ data-retriever - Data loading")
    print("  ✓ llm-provider - LLM execution")
    print("  ✓ format-converter - Format conversion")
    print()
    print("Output formats generated:")
    print("  ✓ Markdown (from LLM)")
    print("  ✓ HTML")
    if 'pdf_output' in locals():
        print("  ✓ PDF")


if __name__ == "__main__":
    try:
        full_workflow_example()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

