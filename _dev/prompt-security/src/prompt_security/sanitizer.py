"""
Input Sanitizer

Sanitizes user input by removing or escaping dangerous content.
"""

import re
from typing import Dict, Any
from .config import SecurityConfig


class InputSanitizer:
    """Sanitizes user input according to security configuration."""
    
    def __init__(self, config: SecurityConfig):
        """
        Initialize sanitizer.
        
        Args:
            config: Security configuration
        """
        self.config = config
    
    def sanitize(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize user input dictionary.
        
        Args:
            user_input: Dictionary of user-provided values
            
        Returns:
            Sanitized dictionary
        """
        sanitized = {}
        
        for key, value in user_input.items():
            # Convert to string
            if not isinstance(value, str):
                value_str = str(value)
            else:
                value_str = value
            
            # Apply sanitization
            sanitized_value = self._sanitize_string(value_str)
            sanitized[key] = sanitized_value
        
        return sanitized
    
    def _sanitize_string(self, text: str) -> str:
        """
        Sanitize a single string value.
        
        Args:
            text: Input text to sanitize
            
        Returns:
            Sanitized text
        """
        # Remove control characters (except allowed ones)
        if not self.config.allow_control_chars:
            text = self._remove_control_chars(text)
        
        # Handle newlines
        if not self.config.allow_newlines:
            text = text.replace('\n', ' ').replace('\r', ' ')
        
        # Truncate if too long
        if len(text) > self.config.max_length:
            text = text[:self.config.max_length]
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def _remove_control_chars(self, text: str) -> str:
        """Remove control characters from text."""
        # Keep common whitespace: space, tab, newline, carriage return
        # Remove other control characters
        result = []
        for char in text:
            ord_val = ord(char)
            # Keep printable ASCII (32-126) and common whitespace
            if ord_val >= 32 or char in ['\n', '\r', '\t']:
                result.append(char)
        return ''.join(result)

