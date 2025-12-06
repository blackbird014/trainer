"""Tests for JSON to Markdown converter."""

import pytest
from format_converter.converters.json_to_markdown import JSONToMarkdownConverter


def test_simple_dict():
    """Test converting simple dictionary."""
    converter = JSONToMarkdownConverter()
    data = {"title": "Report", "content": "This is content"}
    md = converter.convert(data)
    assert "Report" in md
    assert "content" in md.lower() or "Content" in md


def test_nested_dict():
    """Test converting nested dictionary."""
    converter = JSONToMarkdownConverter()
    data = {
        "report": {
            "summary": "Summary text",
            "details": {
                "section1": "Detail 1",
                "section2": "Detail 2"
            }
        }
    }
    md = converter.convert(data)
    assert "report" in md.lower() or "Report" in md
    assert "summary" in md.lower() or "Summary" in md


def test_list_to_table():
    """Test converting list of dicts to table."""
    converter = JSONToMarkdownConverter()
    data = {
        "companies": [
            {"name": "AAPL", "price": 150},
            {"name": "NVDA", "price": 500}
        ]
    }
    md = converter.convert(data)
    assert "AAPL" in md
    assert "NVDA" in md
    assert "|" in md  # Should have table


def test_simple_list():
    """Test converting simple list."""
    converter = JSONToMarkdownConverter()
    data = {"items": ["Item 1", "Item 2", "Item 3"]}
    md = converter.convert(data)
    assert "Item 1" in md
    assert "Item 2" in md


def test_with_title():
    """Test conversion with title option."""
    converter = JSONToMarkdownConverter()
    data = {"key": "value"}
    md = converter.convert(data, title="My Report")
    assert "# My Report" in md

