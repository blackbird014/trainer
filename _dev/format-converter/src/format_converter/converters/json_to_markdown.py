"""
JSON to Markdown converter (schema-aware).
"""

from typing import Dict, Any, Optional, List


class JSONToMarkdownConverter:
    """Convert JSON structure to Markdown (schema-aware)."""

    def __init__(self, schema: Optional[Any] = None):
        """
        Initialize converter.

        Args:
            schema: Optional schema to guide conversion
        """
        self.schema = schema

    def convert(self, json_data: Dict[str, Any], **options) -> str:
        """
        Convert JSON to Markdown.

        Args:
            json_data: JSON data to convert
            **options: Additional options:
                - title: Document title
                - level: Starting heading level (default: 1)

        Returns:
            Markdown string
        """
        level = options.get('level', 1)
        title = options.get('title')

        markdown_parts = []

        if title:
            markdown_parts.append(f"{'#' * level} {title}\n")

        markdown_parts.append(self._convert_value(json_data, level + 1))

        return "\n".join(markdown_parts)

    def _convert_value(self, value: Any, level: int = 1) -> str:
        """Convert a JSON value to markdown."""
        if isinstance(value, dict):
            return self._convert_dict(value, level)
        elif isinstance(value, list):
            return self._convert_list(value, level)
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, bool):
            return "Yes" if value else "No"
        elif value is None:
            return "*N/A*"
        else:
            return str(value)

    def _convert_dict(self, data: Dict[str, Any], level: int) -> str:
        """Convert dictionary to markdown sections."""
        parts = []

        for key, value in data.items():
            # Format key as header or bold text
            key_formatted = self._format_key(key)

            if isinstance(value, dict):
                parts.append(f"{'#' * level} {key_formatted}\n")
                parts.append(self._convert_dict(value, level + 1))
            elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                # List of objects -> table
                parts.append(f"{'#' * level} {key_formatted}\n")
                parts.append(self._convert_list_to_table(value))
            elif isinstance(value, list):
                # Simple list
                parts.append(f"{'#' * level} {key_formatted}\n")
                parts.append(self._convert_list(value, level + 1))
            else:
                # Simple key-value
                parts.append(f"**{key_formatted}**: {self._convert_value(value, level)}\n")

        return "\n".join(parts)

    def _convert_list(self, items: List[Any], level: int) -> str:
        """Convert list to markdown."""
        parts = []
        for item in items:
            if isinstance(item, dict):
                parts.append(self._convert_dict(item, level))
            else:
                parts.append(f"- {self._convert_value(item, level)}")
        return "\n".join(parts)

    def _convert_list_to_table(self, items: List[Dict[str, Any]]) -> str:
        """Convert list of dicts to markdown table."""
        if not items:
            return ""

        # Get all keys from all items
        all_keys = set()
        for item in items:
            all_keys.update(item.keys())

        keys = sorted(all_keys)

        # Build table
        parts = []
        # Header
        parts.append("| " + " | ".join(self._format_key(k) for k in keys) + " |")
        parts.append("| " + " | ".join(["---"] * len(keys)) + " |")

        # Rows
        for item in items:
            row = []
            for key in keys:
                value = item.get(key, "")
                row.append(str(value) if value is not None else "*N/A*")
            parts.append("| " + " | ".join(row) + " |")

        return "\n".join(parts)

    def _format_key(self, key: str) -> str:
        """Format key name for display."""
        # Convert snake_case to Title Case
        return key.replace("_", " ").title()

