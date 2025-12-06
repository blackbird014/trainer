"""
Format detection for auto-detecting input format (MD vs JSON).
"""

import json
import re
from typing import Union, Dict, Any


class FormatDetector:
    """Detects the format of input content."""

    # Markdown patterns
    MD_PATTERNS = [
        r'^#{1,6}\s+',  # Headers
        r'^\s*[-*+]\s+',  # Unordered lists
        r'^\s*\d+\.\s+',  # Ordered lists
        r'\|.*\|',  # Tables
        r'\[.*\]\(.*\)',  # Links
        r'\*\*.*\*\*',  # Bold
        r'_.*_',  # Italic
        r'```',  # Code blocks
    ]

    @staticmethod
    def detect(content: Union[str, Dict[str, Any]]) -> str:
        """
        Detect format of input content.

        Args:
            content: Content to detect (string or dict)

        Returns:
            Format string: "json", "markdown", "text", or "unknown"
        """
        # If already a dict, it's JSON
        if isinstance(content, dict):
            return "json"

        # If not a string, convert to string
        if not isinstance(content, str):
            content = str(content)

        # Try parsing as JSON first
        if FormatDetector._is_json(content):
            return "json"

        # Check for markdown patterns
        if FormatDetector._is_markdown(content):
            return "markdown"

        # Default to text
        return "text"

    @staticmethod
    def _is_json(content: str) -> bool:
        """Check if content is valid JSON."""
        content = content.strip()

        # Quick check: must start with { or [
        if not (content.startswith("{") or content.startswith("[")):
            # Check if it's JSON wrapped in markdown code block
            json_match = re.search(r'```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)

        # Try parsing
        try:
            json.loads(content)
            return True
        except (json.JSONDecodeError, ValueError):
            return False

    @staticmethod
    def _is_markdown(content: str) -> bool:
        """Check if content looks like markdown."""
        lines = content.split("\n")[:10]  # Check first 10 lines

        markdown_score = 0
        for pattern in FormatDetector.MD_PATTERNS:
            for line in lines:
                if re.search(pattern, line):
                    markdown_score += 1
                    break

        # If we found at least 1 markdown pattern, consider it markdown
        # (Lower threshold to catch simple markdown like "# Title")
        return markdown_score >= 1

    @staticmethod
    def extract_json_from_text(text: str) -> Dict[str, Any]:
        """
        Extract JSON from text (handles code blocks, etc.).

        Args:
            text: Text that may contain JSON

        Returns:
            Parsed JSON dict, or None if not found
        """
        text = text.strip()

        # Try direct parsing first
        try:
            return json.loads(text)
        except (json.JSONDecodeError, ValueError):
            pass

        # Try extracting from markdown code blocks
        json_patterns = [
            r'```(?:json)?\s*(\{.*?\})\s*```',  # JSON in code block
            r'```(?:json)?\s*(\[.*?\])\s*```',  # JSON array in code block
            r'(\{.*\})',  # Any JSON object
            r'(\[.*\])',  # Any JSON array
        ]

        for pattern in json_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except (json.JSONDecodeError, ValueError):
                    continue

        return None

