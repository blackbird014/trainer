"""
Template Escaper

Safely escapes user input for template insertion.
"""

from typing import Optional
from .config import SecurityConfig


class TemplateEscaper:
    """Escapes user input for safe template insertion."""
    
    def __init__(self, config: SecurityConfig):
        """
        Initialize escaper.
        
        Args:
            config: Security configuration
        """
        self.config = config
    
    def escape(self, text: str, context: str = "template") -> str:
        """
        Escape text for safe insertion into template.
        
        Args:
            text: Text to escape
            context: Context where text will be inserted
            
        Returns:
            Escaped text with appropriate delimiters
        """
        if self.config.escape_mode == "xml":
            return self._escape_xml(text)
        elif self.config.escape_mode == "json":
            return self._escape_json(text)
        elif self.config.escape_mode == "delimiter":
            return self._escape_delimiter(text)
        else:
            return text
    
    def _escape_xml(self, text: str) -> str:
        """Escape using XML-style tags."""
        # Escape XML special characters
        escaped = text.replace('&', '&amp;')
        escaped = escaped.replace('<', '&lt;')
        escaped = escaped.replace('>', '&gt;')
        escaped = escaped.replace('"', '&quot;')
        escaped = escaped.replace("'", '&apos;')
        
        if self.config.use_delimiters:
            return f"<user_input>{escaped}</user_input>"
        return escaped
    
    def _escape_json(self, text: str) -> str:
        """Escape using JSON encoding."""
        import json
        # JSON encode the text
        escaped = json.dumps(text)
        
        if self.config.use_delimiters:
            return f'{{"user_input": {escaped}}}'
        return escaped
    
    def _escape_delimiter(self, text: str) -> str:
        """Escape using explicit delimiters."""
        # Escape the delimiter characters if present
        escaped = text.replace('[USER_DATA_START]', '\\[USER_DATA_START\\]')
        escaped = escaped.replace('[USER_DATA_END]', '\\[USER_DATA_END]')
        
        if self.config.use_delimiters:
            return f"[USER_DATA_START]{escaped}[USER_DATA_END]"
        return escaped
    
    def wrap_user_section(self, text: str, section_name: str = "user_data") -> str:
        """
        Wrap text in a user data section with explicit markers.
        
        Args:
            text: Text to wrap
            section_name: Name of the section
            
        Returns:
            Wrapped text with clear boundaries
        """
        return f"\n\n--- USER INPUT SECTION: {section_name} ---\n{text}\n--- END USER INPUT ---\n\n"

