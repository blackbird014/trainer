"""
Input Validator

Validates user input for length, characters, and types.
"""

import re
from typing import Dict, Any, List
from .security_result import ValidationResult
from .config import SecurityConfig


class InputValidator:
    """Validates user input according to security configuration."""
    
    def __init__(self, config: SecurityConfig):
        """
        Initialize validator.
        
        Args:
            config: Security configuration
        """
        self.config = config
    
    def validate(self, user_input: Dict[str, Any]) -> ValidationResult:
        """
        Validate user input dictionary.
        
        Args:
            user_input: Dictionary of user-provided values
            
        Returns:
            ValidationResult with validation status and details
        """
        result = ValidationResult(is_valid=True)
        sanitized = {}
        
        for key, value in user_input.items():
            # Convert value to string for validation
            if not isinstance(value, str):
                value_str = str(value)
            else:
                value_str = value
            
            # Validate length
            length_result = self._validate_length(value_str, key)
            if not length_result.is_valid:
                result.add_error(f"{key}: {length_result.errors[0]}")
                continue
            
            # Validate characters
            char_result = self._validate_characters(value_str, key)
            if not char_result.is_valid:
                result.add_error(f"{key}: {char_result.errors[0]}")
                continue
            
            # Add warnings
            if length_result.warnings:
                result.warnings.extend([f"{key}: {w}" for w in length_result.warnings])
            if char_result.warnings:
                result.warnings.extend([f"{key}: {w}" for w in char_result.warnings])
            
            # Store sanitized value
            sanitized[key] = value_str
        
        result.sanitized_input = sanitized
        result.validation_details = {
            "validated_keys": list(sanitized.keys()),
            "total_keys": len(user_input),
        }
        
        return result
    
    def _validate_length(self, value: str, key: str) -> ValidationResult:
        """Validate input length."""
        result = ValidationResult(is_valid=True)
        length = len(value)
        
        if length < self.config.min_length:
            result.add_error(
                f"Value too short: {length} chars (minimum: {self.config.min_length})"
            )
        
        if length > self.config.max_length:
            result.add_error(
                f"Value too long: {length} chars (maximum: {self.config.max_length})"
            )
        
        # Warning for values approaching limit
        if length > self.config.max_length * 0.9:
            result.add_warning(
                f"Value approaching length limit: {length}/{self.config.max_length} chars"
            )
        
        return result
    
    def _validate_characters(self, value: str, key: str) -> ValidationResult:
        """Validate allowed characters."""
        result = ValidationResult(is_valid=True)
        
        # Check for control characters
        if not self.config.allow_control_chars:
            control_chars = self._find_control_chars(value)
            if control_chars:
                if self.config.strict_mode:
                    result.add_error(
                        f"Control characters not allowed: {', '.join(repr(c) for c in control_chars[:5])}"
                    )
                else:
                    result.add_warning(
                        f"Control characters detected: {', '.join(repr(c) for c in control_chars[:5])}"
                    )
        
        # Check for newlines
        if not self.config.allow_newlines:
            if '\n' in value or '\r' in value:
                if self.config.strict_mode:
                    result.add_error("Newlines not allowed in user input")
                else:
                    result.add_warning("Newlines detected in user input")
        
        # Check against allowed pattern if specified
        if self.config.allowed_chars_pattern:
            pattern = re.compile(self.config.allowed_chars_pattern)
            invalid_chars = [c for c in value if not pattern.match(c)]
            if invalid_chars:
                unique_invalid = list(set(invalid_chars))[:5]
                result.add_error(
                    f"Invalid characters: {', '.join(repr(c) for c in unique_invalid)}"
                )
        
        return result
    
    def _find_control_chars(self, text: str) -> List[str]:
        """Find control characters in text."""
        control_chars = []
        for char in text:
            if ord(char) < 32 and char not in ['\n', '\r', '\t']:
                control_chars.append(char)
        return list(set(control_chars))

