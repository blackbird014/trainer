"""
JSON extraction from text (handles code blocks, etc.).
"""

from typing import Dict, Any, Optional
from format_converter.detector import FormatDetector


class JSONExtractor:
    """Extract JSON from text content."""

    @staticmethod
    def extract(text: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from text.

        Args:
            text: Text that may contain JSON

        Returns:
            Parsed JSON dict/array, or None if not found
        """
        return FormatDetector.extract_json_from_text(text)

    @staticmethod
    def is_json_response(text: str) -> bool:
        """
        Check if text appears to be a JSON response from LLM.

        Args:
            text: Text to check

        Returns:
            True if text contains JSON
        """
        return FormatDetector.extract_json_from_text(text) is not None

