"""Tests for FormatConverter."""

import pytest
from format_converter import FormatConverter


def test_converter_init():
    """Test converter initialization."""
    converter = FormatConverter()
    assert converter.enable_metrics is True


def test_markdown_to_html():
    """Test markdown to HTML conversion."""
    converter = FormatConverter(enable_metrics=False)
    md = "# Title\n\nThis is **bold** text."
    html = converter.convert(md, source_format="markdown", target_format="html")
    assert "<h1>Title</h1>" in html or "Title" in html
    assert "bold" in html.lower()


def test_json_to_markdown():
    """Test JSON to markdown conversion."""
    converter = FormatConverter(enable_metrics=False)
    json_data = {
        "title": "Report",
        "sections": {
            "summary": "This is a summary",
            "details": ["Detail 1", "Detail 2"]
        }
    }
    md = converter.convert(json_data, source_format="json", target_format="markdown")
    assert "Report" in md
    assert "summary" in md.lower() or "Summary" in md


def test_auto_detection():
    """Test auto-detection of format."""
    converter = FormatConverter(enable_metrics=False)
    
    # Test markdown detection
    md = "# Title\n\nContent"
    html = converter.convert(md, source_format="auto", target_format="html")
    assert isinstance(html, str)
    
    # Test JSON detection
    json_str = '{"key": "value"}'
    md = converter.convert(json_str, source_format="auto", target_format="markdown")
    assert isinstance(md, str)


def test_markdown_to_json():
    """Test markdown to JSON conversion."""
    converter = FormatConverter(enable_metrics=False)
    md = """# Title

## Section 1

Content here

## Section 2

More content
"""
    json_data = converter.convert(md, source_format="markdown", target_format="json")
    assert isinstance(json_data, dict)
    assert "title" in json_data.get("content", {})


def test_unsupported_conversion():
    """Test error handling for unsupported conversion."""
    converter = FormatConverter(enable_metrics=False)
    with pytest.raises(ValueError):
        converter.convert("test", source_format="text", target_format="unknown")


def test_detect_format():
    """Test format detection method."""
    converter = FormatConverter(enable_metrics=False)
    
    assert converter.detect_format("# Title") == "markdown"
    assert converter.detect_format('{"key": "value"}') == "json"
    assert converter.detect_format({"key": "value"}) == "json"


def test_extract_json_from_text():
    """Test JSON extraction from text."""
    converter = FormatConverter(enable_metrics=False)
    
    text = 'Here is JSON: {"key": "value"}'
    json_data = converter.extract_json_from_text(text)
    assert json_data == {"key": "value"}

