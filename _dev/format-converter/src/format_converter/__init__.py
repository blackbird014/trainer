"""
Format Conversion System

Provides conversion between different formats (Markdown, HTML, PDF, JSON) with:
- Auto-detection of input format
- Schema-aware JSON conversion
- Bidirectional MD ↔ JSON conversion
- Structured output support for LLM responses
"""

from format_converter.converter import FormatConverter
from format_converter.detector import FormatDetector
from format_converter.metrics import MetricsCollector

__all__ = [
    "FormatConverter",
    "FormatDetector",
    "MetricsCollector",
]

__version__ = "0.1.0"

