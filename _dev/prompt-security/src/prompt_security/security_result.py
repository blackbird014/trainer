"""
Security Result Types

Defines result types for security operations.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class DetectionResult:
    """Result of prompt injection detection."""
    
    is_safe: bool
    confidence: float  # 0.0 to 1.0
    flags: List[str] = field(default_factory=list)
    risk_score: float = 0.0  # 0.0 to 1.0
    recommendations: List[str] = field(default_factory=list)
    detected_patterns: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate result data."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        if not 0.0 <= self.risk_score <= 1.0:
            raise ValueError(f"Risk score must be between 0.0 and 1.0, got {self.risk_score}")


@dataclass
class ValidationResult:
    """Result of input validation."""
    
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    sanitized_input: Optional[Dict[str, Any]] = None
    validation_details: Dict[str, Any] = field(default_factory=dict)
    
    def add_error(self, error: str):
        """Add a validation error."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Add a validation warning."""
        self.warnings.append(warning)


class SecurityError(Exception):
    """Base exception for security-related errors."""
    pass


class InjectionDetectedError(SecurityError):
    """Raised when prompt injection is detected."""
    
    def __init__(self, message: str, detection_result: DetectionResult):
        super().__init__(message)
        self.detection_result = detection_result


class ValidationError(SecurityError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, validation_result: ValidationResult):
        super().__init__(message)
        self.validation_result = validation_result

