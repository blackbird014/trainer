"""
Markdown to PDF converter.
"""

from typing import Optional
from format_converter.converters.markdown_to_html import MarkdownToHTMLConverter


class MarkdownToPDFConverter:
    """Convert Markdown to PDF."""

    def __init__(self, css_path: Optional[str] = None):
        """
        Initialize converter.

        Args:
            css_path: Optional path to CSS file
        """
        self.css_path = css_path
        self.html_converter = MarkdownToHTMLConverter(css_path=css_path)

    def convert(self, markdown: str, **options) -> bytes:
        """
        Convert markdown to PDF.

        Args:
            markdown: Markdown content
            **options: Additional options (passed to HTML converter)

        Returns:
            PDF bytes
        """
        # First convert to HTML
        html = self.html_converter.convert(markdown, **options)

        # Then convert HTML to PDF using WeasyPrint
        try:
            from weasyprint import HTML
            pdf_bytes = HTML(string=html).write_pdf()
            return pdf_bytes
        except ImportError:
            raise ImportError(
                "WeasyPrint is required for PDF conversion. "
                "Install with: pip install weasyprint"
            )

