"""Tests for format detection."""

import pytest

from format_converter.detector import FormatDetector


def test_detect_json_dict():
    """Test detecting JSON from dict."""
    data = {"key": "value"}
    assert FormatDetector.detect(data) == "json"


def test_detect_json_string():
    """Test detecting JSON from string."""
    json_str = '{"key": "value", "number": 42}'
    assert FormatDetector.detect(json_str) == "json"


def test_detect_json_array():
    """Test detecting JSON array."""
    json_str = '[{"key": "value"}, {"key2": "value2"}]'
    assert FormatDetector.detect(json_str) == "json"


def test_detect_markdown():
    """Test detecting markdown."""
    md = """# Title

## Section

- Item 1
- Item 2

| Col1 | Col2 |
|------|------|
| Val1 | Val2 |
"""
    assert FormatDetector.detect(md) == "markdown"


def test_detect_text():
    """Test detecting plain text."""
    text = "This is just plain text without any special formatting."
    assert FormatDetector.detect(text) == "text"


def test_extract_json_from_code_block():
    """Test extracting JSON from markdown code block."""
    text = """
Here is some JSON:

```json
{"key": "value", "number": 42}
```
"""
    result = FormatDetector.extract_json_from_text(text)
    assert result == {"key": "value", "number": 42}


def test_extract_json_direct():
    """Test extracting JSON directly."""
    json_str = '{"key": "value"}'
    result = FormatDetector.extract_json_from_text(json_str)
    assert result == {"key": "value"}


def test_extract_json_not_found():
    """Test extracting JSON when none exists."""
    text = "This is just plain text."
    result = FormatDetector.extract_json_from_text(text)
    assert result is None

