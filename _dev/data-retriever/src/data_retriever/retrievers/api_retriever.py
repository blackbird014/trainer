"""
Generic REST API retriever.
"""

from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from data_retriever.base import DataRetriever, RetrievalResult
from data_retriever.schema import API_RETRIEVER_SCHEMA, Schema


class APIRetriever(DataRetriever):
    """Generic REST API retriever."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        max_retries: int = 3,
        **kwargs,
    ):
        """
        Initialize API retriever.

        Args:
            base_url: Base URL for API requests
            headers: Default headers for requests
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            **kwargs: Additional arguments passed to DataRetriever
        """
        super().__init__(source_name="api", **kwargs)
        self.base_url = base_url
        self.headers = headers or {}
        self.timeout = timeout
        self.max_retries = max_retries

        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def retrieve(self, query: Dict[str, Any]) -> RetrievalResult:
        """
        Retrieve data from API.

        Query parameters:
            - url: API endpoint URL (or path if base_url is set)
            - method: HTTP method (default: 'GET')
            - params: Query parameters
            - data: Request body data
            - headers: Additional headers
            - timeout: Request timeout (overrides default)

        Returns:
            RetrievalResult with API response data
        """
        try:
            # Build URL
            url = query.get("url")
            if not url:
                return RetrievalResult(
                    data={},
                    source=self.source_name,
                    success=False,
                    error="Missing required parameter: url",
                )

            if self.base_url and not url.startswith(("http://", "https://")):
                url = f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"

            # Request parameters
            method = query.get("method", "GET").upper()
            params = query.get("params", {})
            data = query.get("data")
            headers = {**self.headers, **query.get("headers", {})}
            timeout = query.get("timeout", self.timeout)

            # Make request
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data if isinstance(data, dict) else None,
                data=data if not isinstance(data, dict) else None,
                headers=headers,
                timeout=timeout,
            )

            # Parse response
            try:
                response_data = response.json()
            except ValueError:
                response_data = {"text": response.text}

            # Check for errors
            if not response.ok:
                return RetrievalResult(
                    data={
                        "url": url,
                        "data": response_data,
                        "status_code": response.status_code,
                    },
                    source=self.source_name,
                    success=False,
                    error=f"API request failed: {response.status_code}",
                    metadata={
                        "status_code": response.status_code,
                        "headers": dict(response.headers),
                    },
                )

            return RetrievalResult(
                data={
                    "url": url,
                    "data": response_data,
                    "status_code": response.status_code,
                },
                source=self.source_name,
                metadata={
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "elapsed": response.elapsed.total_seconds(),
                },
            )

        except requests.exceptions.RequestException as e:
            return RetrievalResult(
                data={},
                source=self.source_name,
                success=False,
                error=f"API request error: {str(e)}",
            )
        except Exception as e:
            return RetrievalResult(
                data={},
                source=self.source_name,
                success=False,
                error=f"Unexpected error: {str(e)}",
            )

    def get_schema(self) -> Schema:
        """Get schema for API data."""
        return API_RETRIEVER_SCHEMA

