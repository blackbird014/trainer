"""
Main format converter class.
"""

import time
from typing import Union, Dict, Any, Optional
from pathlib import Path

from format_converter.detector import FormatDetector
from format_converter.metrics import MetricsCollector
from format_converter.converters.markdown_to_html import MarkdownToHTMLConverter
from format_converter.converters.markdown_to_pdf import MarkdownToPDFConverter
from format_converter.converters.json_to_markdown import JSONToMarkdownConverter
from format_converter.converters.markdown_to_json import MarkdownToJSONConverter
from format_converter.converters.json_extractor import JSONExtractor


class FormatConverter:
    """
    Main format converter supporting multiple formats with auto-detection.
    """

    def __init__(self, enable_metrics: bool = True, css_path: Optional[str] = None):
        """
        Initialize format converter.

        Args:
            enable_metrics: Enable Prometheus metrics
            css_path: Default CSS path for HTML/PDF conversion
        """
        self.enable_metrics = enable_metrics
        self.css_path = css_path
        self.metrics = MetricsCollector() if enable_metrics else None

        # Initialize converters
        self.md_to_html = MarkdownToHTMLConverter(css_path=css_path)
        self.md_to_pdf = MarkdownToPDFConverter(css_path=css_path)
        self.json_to_md = JSONToMarkdownConverter()
        self.md_to_json = MarkdownToJSONConverter()
        self.json_extractor = JSONExtractor()

    def convert(
        self,
        source: Union[str, Dict[str, Any]],
        source_format: str = "auto",
        target_format: str = "html",
        **options
    ) -> Union[str, bytes]:
        """
        Convert content from source format to target format.

        Args:
            source: Source content (string or dict)
            source_format: Source format ("auto", "markdown", "json", "text")
            target_format: Target format ("html", "pdf", "markdown", "json")
            **options: Additional options (css_path, template, title, etc.)

        Returns:
            Converted content (string for text formats, bytes for PDF)

        Raises:
            ValueError: If conversion is not supported
        """
        start_time = time.time()

        try:
            # Auto-detect format if needed
            if source_format == "auto":
                detected = FormatDetector.detect(source)
                source_format = detected
                if self.metrics:
                    self.metrics.track_auto_detection(detected)

            # Handle JSON extraction if source is text but detected as JSON
            if source_format == "json" and isinstance(source, str):
                json_data = self.json_extractor.extract(source)
                if json_data:
                    source = json_data
                else:
                    raise ValueError(f"Could not extract JSON from text")

            # Perform conversion
            result = self._perform_conversion(source, source_format, target_format, **options)

            # Track metrics
            duration = time.time() - start_time
            if self.metrics:
                self.metrics.track_operation(source_format, target_format, "success")
                self.metrics.track_duration(source_format, target_format, duration)

                # Track data size
                if isinstance(result, str):
                    size_bytes = len(result.encode('utf-8'))
                else:
                    size_bytes = len(result)
                self.metrics.track_data_size(source_format, target_format, size_bytes)

            return result

        except Exception as e:
            # Track error
            if self.metrics:
                error_type = type(e).__name__
                self.metrics.track_error(source_format, target_format, error_type)
                self.metrics.track_operation(source_format, target_format, "error")

            raise

    def _perform_conversion(
        self,
        source: Union[str, Dict[str, Any]],
        source_format: str,
        target_format: str,
        **options
    ) -> Union[str, bytes]:
        """Perform the actual conversion."""
        # Handle JSON → Markdown → HTML/PDF pipeline
        if source_format == "json" and target_format in ["html", "pdf"]:
            # Convert JSON → MD first
            markdown = self.json_to_markdown(source, **options)
            # Then MD → target
            if target_format == "html":
                return self.md_to_html.convert(markdown, **options)
            elif target_format == "pdf":
                return self.md_to_pdf.convert(markdown, **options)

        # Direct conversions
        if source_format == "markdown":
            if target_format == "html":
                return self.md_to_html.convert(source, **options)
            elif target_format == "pdf":
                return self.md_to_pdf.convert(source, **options)
            elif target_format == "json":
                return self.md_to_json.convert(source, **options)

        elif source_format == "json":
            if target_format == "markdown":
                return self.json_to_markdown(source, **options)
            elif target_format == "html":
                markdown = self.json_to_markdown(source, **options)
                return self.md_to_html.convert(markdown, **options)
            elif target_format == "pdf":
                markdown = self.json_to_markdown(source, **options)
                return self.md_to_pdf.convert(markdown, **options)

        elif source_format == "html" and target_format == "pdf":
            # HTML → PDF
            try:
                from weasyprint import HTML
                return HTML(string=source).write_pdf()
            except ImportError:
                raise ImportError("WeasyPrint required for HTML→PDF conversion")

        elif source_format == "text":
            # Treat text as markdown for conversion
            if target_format in ["html", "pdf"]:
                return self._perform_conversion(source, "markdown", target_format, **options)
            elif target_format == "markdown":
                return source  # Already markdown-like
            else:
                raise ValueError(f"Cannot convert text to {target_format}")

        raise ValueError(
            f"Unsupported conversion: {source_format} → {target_format}"
        )

    def json_to_markdown(
        self,
        json_data: Dict[str, Any],
        schema: Optional[Any] = None,
        template: Optional[str] = None,
        **options
    ) -> str:
        """
        Convert JSON to Markdown (schema-aware).

        Args:
            json_data: JSON data to convert
            schema: Optional schema to guide conversion
            template: Optional template path
            **options: Additional options

        Returns:
            Markdown string
        """
        converter = JSONToMarkdownConverter(schema=schema)
        return converter.convert(json_data, **options)

    def markdown_to_json(
        self,
        markdown: str,
        schema: Optional[Any] = None,
        **options
    ) -> Dict[str, Any]:
        """
        Convert Markdown to JSON (heuristic-based).

        Args:
            markdown: Markdown content
            schema: Optional schema (not yet used, for future)
            **options: Additional options

        Returns:
            JSON dictionary
        """
        return self.md_to_json.convert(markdown, **options)

    def detect_format(self, content: Union[str, Dict[str, Any]]) -> str:
        """
        Auto-detect format of content.

        Args:
            content: Content to detect

        Returns:
            Format string
        """
        return FormatDetector.detect(content)

    def extract_json_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from text (handles code blocks, etc.).

        Args:
            text: Text that may contain JSON

        Returns:
            Parsed JSON dict, or None if not found
        """
        return self.json_extractor.extract(text)

