#!/usr/bin/env python3
"""
Basic usage examples for format-converter module.
"""

from format_converter import FormatConverter


def example_markdown_to_html():
    """Example: Convert Markdown to HTML."""
    print("=" * 60)
    print("Markdown to HTML Example")
    print("=" * 60)

    converter = FormatConverter(enable_metrics=False)
    md = """# Stock Analysis Report

## Summary

This is a **comprehensive** analysis of the stock market.

### Key Metrics

| Metric | Value |
|--------|-------|
| Market Cap | 4.42T |
| P/E Ratio | 26.95 |
"""

    html = converter.convert(md, source_format="markdown", target_format="html")
    print(f"✓ Converted Markdown to HTML ({len(html)} bytes)")
    print(f"  Preview: {html[:100]}...")


def example_json_to_markdown():
    """Example: Convert JSON to Markdown."""
    print("\n" + "=" * 60)
    print("JSON to Markdown Example")
    print("=" * 60)

    converter = FormatConverter(enable_metrics=False)
    json_data = {
        "report": {
            "title": "Stock Analysis",
            "companies": [
                {"ticker": "AAPL", "market_cap": "3.95T", "pe": 35.85},
                {"ticker": "NVDA", "market_cap": "4.42T", "pe": 26.95}
            ],
            "summary": "Market analysis complete"
        }
    }

    md = converter.convert(json_data, source_format="json", target_format="markdown")
    print(f"✓ Converted JSON to Markdown ({len(md)} bytes)")
    print(f"  Preview:\n{md[:200]}...")


def example_auto_detection():
    """Example: Auto-detection of format."""
    print("\n" + "=" * 60)
    print("Auto-Detection Example")
    print("=" * 60)

    converter = FormatConverter(enable_metrics=False)

    # Markdown content
    md_content = "# Title\n\nContent here"
    detected = converter.detect_format(md_content)
    print(f"✓ Detected format: {detected} (expected: markdown)")

    # JSON content
    json_content = '{"key": "value"}'
    detected = converter.detect_format(json_content)
    print(f"✓ Detected format: {detected} (expected: json)")

    # Auto-convert
    html = converter.convert(md_content, source_format="auto", target_format="html")
    print(f"✓ Auto-converted to HTML ({len(html)} bytes)")


def example_json_extraction():
    """Example: Extract JSON from LLM response."""
    print("\n" + "=" * 60)
    print("JSON Extraction Example")
    print("=" * 60)

    converter = FormatConverter(enable_metrics=False)

    # Simulated LLM response with JSON in code block
    llm_response = """
Here is the analysis data:

```json
{
  "ticker": "AAPL",
  "metrics": {
    "market_cap": "3.95T",
    "pe_ratio": 35.85
  }
}
```

This concludes the analysis.
"""

    json_data = converter.extract_json_from_text(llm_response)
    if json_data:
        print(f"✓ Extracted JSON: {json_data}")
        # Convert to markdown
        md = converter.convert(json_data, source_format="json", target_format="markdown")
        print(f"✓ Converted to Markdown ({len(md)} bytes)")
    else:
        print("✗ No JSON found in text")


if __name__ == "__main__":
    try:
        example_markdown_to_html()
        example_json_to_markdown()
        example_auto_detection()
        example_json_extraction()
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()

