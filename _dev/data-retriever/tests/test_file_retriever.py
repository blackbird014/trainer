"""Tests for FileRetriever."""

import json
import tempfile
from pathlib import Path

import pytest

from data_retriever.retrievers.file_retriever import FileRetriever


def test_file_retriever_init():
    """Test FileRetriever initialization."""
    retriever = FileRetriever()
    assert retriever.source_name == "file"


def test_file_retriever_with_base_path():
    """Test FileRetriever with base path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        retriever = FileRetriever(base_path=tmpdir)
        assert retriever.base_path == Path(tmpdir)


def test_file_retriever_read_json():
    """Test reading JSON file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test JSON file
        test_file = Path(tmpdir) / "test.json"
        test_data = {"key": "value", "number": 42}
        with open(test_file, "w") as f:
            json.dump(test_data, f)

        retriever = FileRetriever(base_path=tmpdir)
        result = retriever.retrieve({"path": "test.json"})

        assert result.success
        assert result.data["content"] == test_data
        assert result.data["format"] == "json"


def test_file_retriever_read_text():
    """Test reading text file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test text file
        test_file = Path(tmpdir) / "test.txt"
        test_content = "Hello, World!"
        with open(test_file, "w") as f:
            f.write(test_content)

        retriever = FileRetriever(base_path=tmpdir)
        result = retriever.retrieve({"path": "test.txt"})

        assert result.success
        assert result.data["content"] == test_content
        assert result.data["format"] == "text"


def test_file_retriever_missing_path():
    """Test FileRetriever with missing path parameter."""
    retriever = FileRetriever()
    result = retriever.retrieve({})

    assert not result.success
    assert "path" in result.error.lower()


def test_file_retriever_nonexistent_file():
    """Test FileRetriever with nonexistent file."""
    retriever = FileRetriever()
    result = retriever.retrieve({"path": "nonexistent.json"})

    assert not result.success
    assert "not found" in result.error.lower()


def test_file_retriever_absolute_path():
    """Test FileRetriever with absolute path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.json"
        test_data = {"key": "value"}
        with open(test_file, "w") as f:
            json.dump(test_data, f)

        retriever = FileRetriever()
        result = retriever.retrieve({"path": str(test_file)})

        assert result.success
        assert result.data["content"] == test_data

