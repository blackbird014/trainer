"""
File-based data retriever for local filesystem.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from data_retriever.base import DataRetriever, RetrievalResult
from data_retriever.schema import FILE_RETRIEVER_SCHEMA, Schema


class FileRetriever(DataRetriever):
    """Retriever for local file system."""

    def __init__(self, base_path: Optional[str] = None, **kwargs):
        """
        Initialize file retriever.

        Args:
            base_path: Base directory for file operations
            **kwargs: Additional arguments passed to DataRetriever
        """
        super().__init__(source_name="file", **kwargs)
        self.base_path = Path(base_path) if base_path else Path.cwd()

    def retrieve(self, query: Dict[str, Any]) -> RetrievalResult:
        """
        Retrieve data from file.

        Query parameters:
            - path: File path (relative to base_path or absolute)
            - format: Optional file format ('json', 'text', 'auto')

        Returns:
            RetrievalResult with file content
        """
        try:
            file_path = query.get("path")
            if not file_path:
                return RetrievalResult(
                    data={},
                    source=self.source_name,
                    success=False,
                    error="Missing required parameter: path",
                )

            # Resolve path
            if os.path.isabs(file_path):
                full_path = Path(file_path)
            else:
                full_path = self.base_path / file_path

            if not full_path.exists():
                return RetrievalResult(
                    data={},
                    source=self.source_name,
                    success=False,
                    error=f"File not found: {full_path}",
                )

            # Determine format
            file_format = query.get("format", "auto")
            if file_format == "auto":
                file_format = self._detect_format(full_path)

            # Read file
            content = self._read_file(full_path, file_format)

            return RetrievalResult(
                data={
                    "path": str(full_path),
                    "content": content,
                    "format": file_format,
                },
                source=self.source_name,
                metadata={
                    "file_size": full_path.stat().st_size,
                    "modified_at": full_path.stat().st_mtime,
                },
            )

        except Exception as e:
            return RetrievalResult(
                data={},
                source=self.source_name,
                success=False,
                error=f"Error reading file: {str(e)}",
            )

    def _detect_format(self, path: Path) -> str:
        """Detect file format from extension."""
        ext = path.suffix.lower()
        if ext == ".json":
            return "json"
        elif ext in [".txt", ".md", ".csv"]:
            return "text"
        else:
            return "text"  # Default

    def _read_file(self, path: Path, file_format: str) -> Any:
        """Read file based on format."""
        with open(path, "r", encoding="utf-8") as f:
            if file_format == "json":
                return json.load(f)
            else:
                return f.read()

    def get_schema(self) -> Schema:
        """Get schema for file data."""
        return FILE_RETRIEVER_SCHEMA

