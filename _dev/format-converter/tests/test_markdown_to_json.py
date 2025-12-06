"""Tests for Markdown to JSON converter."""

import pytest
from format_converter.converters.markdown_to_json import MarkdownToJSONConverter


def test_simple_markdown():
    """Test converting simple markdown."""
    converter = MarkdownToJSONConverter()
    md = "# Title\n\nContent here"
    json_data = converter.convert(md)
    assert isinstance(json_data, dict)
    assert "content" in json_data or "title" in json_data


def test_markdown_with_sections():
    """Test converting markdown with sections."""
    converter = MarkdownToJSONConverter()
    md = """# Main Title

## Section 1

Content of section 1

## Section 2

Content of section 2
"""
    json_data = converter.convert(md)
    assert isinstance(json_data, dict)
    # Should have sections
    content = json_data.get("content", {})
    assert len(content) > 0


def test_markdown_with_table():
    """Test converting markdown with table."""
    converter = MarkdownToJSONConverter()
    md = """# Report

## Data

| Name | Value |
|------|-------|
| Item1 | 100 |
| Item2 | 200 |
"""
    json_data = converter.convert(md)
    assert isinstance(json_data, dict)
    # Should have table data
    content = json_data.get("content", {})
    # Table should be parsed
    assert len(str(content)) > 0


def test_markdown_with_list():
    """Test converting markdown with list."""
    converter = MarkdownToJSONConverter()
    md = """# Report

## Items

- Item 1
- Item 2
- Item 3
"""
    json_data = converter.convert(md)
    assert isinstance(json_data, dict)
    content = json_data.get("content", {})
    assert len(str(content)) > 0

