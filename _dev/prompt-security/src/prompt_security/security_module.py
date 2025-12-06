"""
Security Module

Main security module that orchestrates validation, sanitization, detection, and escaping.
"""

from typing import Dict, Any, Optional
from .config import SecurityConfig
from .validator import InputValidator
from .sanitizer import InputSanitizer
from .detector import InjectionDetector
from .escaper import TemplateEscaper
from .security_result import (
    ValidationResult,
    DetectionResult,
    InjectionDetectedError,
    ValidationError
)


class SecurityModule:
    """
    Main security module for prompt injection protection.
    
    Provides a unified interface for:
    - Input validation
    - Input sanitization
    - Injection detection
    - Template escaping
    """
    
    def __init__(
        self,
        config: Optional[SecurityConfig] = None,
        max_length: int = 1000,
        strict_mode: bool = True,
        enable_ml_detection: bool = False
    ):
        """
        Initialize security module.
        
        Args:
            config: Security configuration (creates default if not provided)
            max_length: Maximum length per variable (if config not provided)
            strict_mode: Enable strict validation (if config not provided)
            enable_ml_detection: Enable ML-based detection (future feature)
        """
        if config is None:
            config = SecurityConfig(
                max_length=max_length,
                strict_mode=strict_mode,
                enable_ml_detection=enable_ml_detection
            )
        
        self.config = config
        self.validator = InputValidator(config)
        self.sanitizer = InputSanitizer(config)
        self.detector = InjectionDetector(config)
        self.escaper = TemplateEscaper(config)
    
    def validate(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate user input.
        
        Args:
            user_input: Dictionary of user-provided values
            
        Returns:
            Validated and sanitized input dictionary
            
        Raises:
            ValidationError: If validation fails in strict mode
        """
        result = self.validator.validate(user_input)
        
        if not result.is_valid:
            if self.config.strict_mode:
                raise ValidationError(
                    f"Input validation failed: {', '.join(result.errors)}",
                    result
                )
            # In non-strict mode, log warnings but continue
        
        # Sanitize the input
        sanitized = self.sanitizer.sanitize(result.sanitized_input or user_input)
        
        return sanitized
    
    def sanitize(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize user input (without validation).
        
        Args:
            user_input: Dictionary of user-provided values
            
        Returns:
            Sanitized input dictionary
        """
        return self.sanitizer.sanitize(user_input)
    
    def detect_injection(self, text: str) -> DetectionResult:
        """
        Detect prompt injection attempts in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            DetectionResult with detection status
        """
        return self.detector.detect(text)
    
    def escape(self, text: str, context: str = "template") -> str:
        """
        Escape text for safe template insertion.
        
        Args:
            text: Text to escape
            context: Context where text will be inserted
            
        Returns:
            Escaped text
        """
        return self.escaper.escape(text, context)
    
    def validate_and_detect(self, user_input: Dict[str, Any]) -> tuple:
        """
        Validate input and detect injections in one operation.
        
        Args:
            user_input: Dictionary of user-provided values
            
        Returns:
            Tuple of (validated_input, detection_result)
            
        Raises:
            ValidationError: If validation fails in strict mode
            InjectionDetectedError: If injection detected in strict mode
        """
        # Validate and sanitize
        validated = self.validate(user_input)
        
        # Detect injections in all values
        all_text = ' '.join(str(v) for v in validated.values())
        detection = self.detect_injection(all_text)
        
        # Check individual values too
        for key, value in validated.items():
            value_detection = self.detect_injection(str(value))
            if not value_detection.is_safe:
                # Merge detections
                detection.flags.extend([f"{key}: {f}" for f in value_detection.flags])
                detection.detected_patterns.extend(value_detection.detected_patterns)
                detection.risk_score = max(detection.risk_score, value_detection.risk_score)
        
        # Recalculate safety
        detection.is_safe = detection.risk_score < self.config.detection_threshold
        
        if not detection.is_safe and self.config.strict_mode:
            raise InjectionDetectedError(
                f"Prompt injection detected: {', '.join(detection.flags[:3])}",
                detection
            )
        
        return validated, detection
    
    def validate_prompt(self, prompt: str) -> ValidationResult:
        """
        Validate a complete prompt before sending to LLM.
        
        Args:
            prompt: Complete prompt text
            
        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult(is_valid=True)
        
        # Check length
        if len(prompt) > self.config.max_length * 10:  # Allow larger prompts
            result.add_warning(f"Prompt is very long: {len(prompt)} chars")
        
        # Detect injections
        detection = self.detect_injection(prompt)
        if not detection.is_safe:
            result.add_warning(
                f"Potential injection detected: {', '.join(detection.flags[:3])}"
            )
            result.validation_details["detection"] = detection
        
        return result

