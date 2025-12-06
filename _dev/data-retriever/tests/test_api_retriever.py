"""Tests for APIRetriever."""

from unittest.mock import Mock, patch

import pytest
import requests

from data_retriever.retrievers.api_retriever import APIRetriever


def test_api_retriever_init():
    """Test APIRetriever initialization."""
    retriever = APIRetriever()
    assert retriever.source_name == "api"
    assert retriever.timeout == 30


def test_api_retriever_with_base_url():
    """Test APIRetriever with base URL."""
    retriever = APIRetriever(base_url="https://api.example.com")
    assert retriever.base_url == "https://api.example.com"


@patch("data_retriever.retrievers.api_retriever.requests.Session")
def test_api_retriever_get_request(mock_session):
    """Test APIRetriever GET request."""
    # Mock response
    mock_response = Mock()
    mock_response.json.return_value = {"status": "ok", "data": "test"}
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.headers = {}
    mock_response.elapsed.total_seconds.return_value = 0.5

    mock_session_instance = Mock()
    mock_session_instance.request.return_value = mock_response
    mock_session.return_value = mock_session_instance

    retriever = APIRetriever()
    retriever.session = mock_session_instance

    result = retriever.retrieve({"url": "https://api.example.com/test"})

    assert result.success
    assert result.data["data"]["status"] == "ok"
    assert result.data["status_code"] == 200


@patch("data_retriever.retrievers.api_retriever.requests.Session")
def test_api_retriever_post_request(mock_session):
    """Test APIRetriever POST request."""
    mock_response = Mock()
    mock_response.json.return_value = {"created": True}
    mock_response.ok = True
    mock_response.status_code = 201
    mock_response.headers = {}
    mock_response.elapsed.total_seconds.return_value = 0.3

    mock_session_instance = Mock()
    mock_session_instance.request.return_value = mock_response
    mock_session.return_value = mock_session_instance

    retriever = APIRetriever()
    retriever.session = mock_session_instance

    result = retriever.retrieve(
        {
            "url": "https://api.example.com/create",
            "method": "POST",
            "data": {"name": "test"},
        }
    )

    assert result.success
    assert result.data["data"]["created"] is True


def test_api_retriever_missing_url():
    """Test APIRetriever with missing URL."""
    retriever = APIRetriever()
    result = retriever.retrieve({})

    assert not result.success
    assert "url" in result.error.lower()


def test_api_retriever_with_base_url_path():
    """Test APIRetriever combining base URL with path."""
    retriever = APIRetriever(base_url="https://api.example.com")

    with patch.object(retriever.session, "request") as mock_request:
        mock_response = Mock()
        mock_response.json.return_value = {"data": "test"}
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.elapsed.total_seconds.return_value = 0.1
        mock_request.return_value = mock_response

        result = retriever.retrieve({"url": "/endpoint"})

        # Check that URL was combined
        call_args = mock_request.call_args
        assert call_args[1]["url"] == "https://api.example.com/endpoint"

