"""
Injection Detector

Detects prompt injection attempts using pattern matching.
"""

import re
from typing import List, Tuple
from .security_result import DetectionResult
from .config import SecurityConfig


class InjectionDetector:
    """Detects prompt injection attempts in user input."""
    
    def __init__(self, config: SecurityConfig):
        """
        Initialize detector.
        
        Args:
            config: Security configuration
        """
        self.config = config
        self.patterns = self._compile_patterns()
    
    def detect(self, text: str) -> DetectionResult:
        """
        Detect prompt injection attempts in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            DetectionResult with detection status and details
        """
        detected_patterns = []
        flags = []
        risk_score = 0.0
        
        # Check against blocked patterns
        for pattern_name, pattern in self.patterns.items():
            matches = pattern.findall(text)
            if matches:
                detected_patterns.append(pattern_name)
                flags.append(f"Matched pattern: {pattern_name}")
                risk_score += 0.3  # Each pattern match increases risk
        
        # Check for instruction-like structures
        instruction_score = self._detect_instruction_patterns(text)
        if instruction_score > 0:
            flags.append("Instruction-like language detected")
            risk_score += instruction_score
        
        # Check for context manipulation attempts
        context_score = self._detect_context_manipulation(text)
        if context_score > 0:
            flags.append("Context manipulation attempt detected")
            risk_score += context_score
        
        # Normalize risk score to 0.0-1.0
        risk_score = min(1.0, risk_score)
        
        # Calculate confidence based on number of flags
        confidence = min(1.0, len(flags) * 0.3)
        if detected_patterns:
            confidence = max(confidence, 0.7)  # High confidence if patterns matched
        
        # Determine if safe
        is_safe = risk_score < self.config.detection_threshold
        
        # Generate recommendations
        recommendations = self._generate_recommendations(flags, risk_score)
        
        return DetectionResult(
            is_safe=is_safe,
            confidence=confidence,
            flags=flags,
            risk_score=risk_score,
            recommendations=recommendations,
            detected_patterns=detected_patterns
        )
    
    def _compile_patterns(self) -> dict:
        """Compile regex patterns for detection."""
        patterns = {}
        for i, pattern_str in enumerate(self.config.blocked_patterns):
            try:
                patterns[f"pattern_{i}"] = re.compile(pattern_str, re.IGNORECASE | re.MULTILINE)
            except re.error as e:
                # Skip invalid patterns
                continue
        return patterns
    
    def _detect_instruction_patterns(self, text: str) -> float:
        """Detect instruction-like language patterns."""
        score = 0.0
        
        # Patterns that suggest instruction override
        instruction_patterns = [
            r"(?i)you\s+(must|should|need\s+to|have\s+to)",
            r"(?i)(do|perform|execute|run)\s+(this|the\s+following)",
            r"(?i)(new|updated|revised)\s+(instruction|prompt|command)",
            r"(?i)from\s+now\s+on",
            r"(?i)change\s+(your|the)\s+(role|behavior|instructions)",
        ]
        
        for pattern_str in instruction_patterns:
            if re.search(pattern_str, text, re.IGNORECASE):
                score += 0.2
        
        return min(0.5, score)  # Cap at 0.5
    
    def _detect_context_manipulation(self, text: str) -> float:
        """Detect attempts to manipulate context."""
        score = 0.0
        
        # Patterns that suggest context manipulation
        context_patterns = [
            r"(?i)(forget|ignore|discard|remove)\s+(previous|earlier|above|all)",
            r"(?i)(clear|reset|delete)\s+(context|memory|history)",
            r"(?i)(start\s+over|begin\s+anew)",
            r"(?i)(pretend|assume|imagine)\s+(that|you\s+are)",
        ]
        
        for pattern_str in context_patterns:
            if re.search(pattern_str, text, re.IGNORECASE):
                score += 0.25
        
        return min(0.4, score)  # Cap at 0.4
    
    def _generate_recommendations(self, flags: List[str], risk_score: float) -> List[str]:
        """Generate security recommendations based on detection."""
        recommendations = []
        
        if risk_score > 0.7:
            recommendations.append("HIGH RISK: Block this input immediately")
        elif risk_score > 0.4:
            recommendations.append("MEDIUM RISK: Review input carefully before processing")
        
        if "Instruction-like language" in ' '.join(flags):
            recommendations.append("Consider using structured templates to isolate user input")
        
        if "Context manipulation" in ' '.join(flags):
            recommendations.append("Ensure system instructions are clearly separated from user input")
        
        if not recommendations:
            recommendations.append("Input appears safe, but continue monitoring")
        
        return recommendations

