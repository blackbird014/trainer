"""
Security Configuration

Configuration for security module behavior.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SecurityConfig:
    """Configuration for security module."""
    
    # Input validation settings
    max_length: int = 1000  # Maximum characters per variable
    min_length: int = 0  # Minimum characters per variable
    strict_mode: bool = True  # Enable strict validation
    
    # Character filtering
    allow_control_chars: bool = False  # Allow control characters
    allow_newlines: bool = False  # Allow newlines in user input
    allowed_chars_pattern: Optional[str] = None  # Regex pattern for allowed chars
    
    # Pattern blocking
    blocked_patterns: List[str] = field(default_factory=lambda: [
        r"(?i)ignore\s+(previous|all|above)",
        r"(?i)forget\s+(previous|all|above)",
        r"(?i)system\s*:",
        r"(?i)###\s*(instruction|system|prompt)\s*:",
        r"(?i)you\s+are\s+now",
        r"(?i)override",
        r"(?i)disregard",
        r"(?i)new\s+instructions",
    ])
    
    # Escaping settings
    escape_mode: str = "xml"  # "xml", "json", "delimiter"
    use_delimiters: bool = True  # Use explicit delimiters for user input
    
    # Detection settings
    detection_threshold: float = 0.7  # Confidence threshold for detection
    enable_ml_detection: bool = False  # Enable ML-based detection (future)
    
    # Logging
    log_security_events: bool = True
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    
    # Rate limiting (future)
    rate_limiting_enabled: bool = False
    requests_per_minute: int = 60
    
    def __post_init__(self):
        """Validate configuration."""
        if self.max_length < 1:
            raise ValueError("max_length must be at least 1")
        if self.min_length < 0:
            raise ValueError("min_length must be non-negative")
        if self.min_length > self.max_length:
            raise ValueError("min_length cannot be greater than max_length")
        if not 0.0 <= self.detection_threshold <= 1.0:
            raise ValueError("detection_threshold must be between 0.0 and 1.0")
        if self.escape_mode not in ["xml", "json", "delimiter"]:
            raise ValueError(f"escape_mode must be one of: xml, json, delimiter")

