"""
Prompt Security Module

Comprehensive security module for protecting against prompt injection attacks
and validating user input in prompt templates.
"""

from .security_module import SecurityModule
from .security_result import (
    DetectionResult,
    ValidationResult,
    SecurityError,
    InjectionDetectedError,
    ValidationError
)
from .validator import InputValidator
from .sanitizer import InputSanitizer
from .detector import InjectionDetector
from .escaper import TemplateEscaper
from .config import SecurityConfig

__all__ = [
    "SecurityModule",
    "DetectionResult",
    "ValidationResult",
    "SecurityError",
    "InjectionDetectedError",
    "ValidationError",
    "InputValidator",
    "InputSanitizer",
    "InjectionDetector",
    "TemplateEscaper",
    "SecurityConfig",
]

__version__ = "0.1.0"

