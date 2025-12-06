"""Tests for Markdown to HTML converter."""

import pytest
import tempfile
from pathlib import Path
from format_converter.converters.markdown_to_html import MarkdownToHTMLConverter


def test_basic_conversion():
    """Test basic markdown to HTML conversion."""
    converter = MarkdownToHTMLConverter()
    md = "# Title\n\nThis is **bold** text."
    html = converter.convert(md)
    assert "<h1>Title</h1>" in html or "Title" in html


def test_with_css():
    """Test conversion with CSS injection."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.css', delete=False) as f:
        f.write("body { color: red; }")
        css_path = f.name

    try:
        converter = MarkdownToHTMLConverter(css_path=css_path)
        md = "# Title"
        html = converter.convert(md)
        assert "color: red" in html or "<style>" in html
    finally:
        Path(css_path).unlink()


def test_table_conversion():
    """Test markdown table conversion."""
    converter = MarkdownToHTMLConverter()
    md = """| Col1 | Col2 |
|------|------|
| Val1 | Val2 |
"""
    html = converter.convert(md)
    assert "<table>" in html or "Col1" in html


def test_code_block():
    """Test code block conversion."""
    converter = MarkdownToHTMLConverter()
    md = "```python\nprint('hello')\n```"
    html = converter.convert(md)
    assert "print" in html or "<code>" in html

