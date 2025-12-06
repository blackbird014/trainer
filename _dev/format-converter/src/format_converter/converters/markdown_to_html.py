"""
Markdown to HTML converter.
"""

import re
from typing import Optional
from pathlib import Path


class MarkdownToHTMLConverter:
    """Convert Markdown to HTML."""

    def __init__(self, css_path: Optional[str] = None):
        """
        Initialize converter.

        Args:
            css_path: Optional path to CSS file to inject
        """
        self.css_path = css_path

    def convert(self, markdown: str, **options) -> str:
        """
        Convert markdown to HTML.

        Args:
            markdown: Markdown content
            **options: Additional options:
                - css_path: Override CSS path
                - template: HTML template path
                - title: Document title

        Returns:
            HTML string
        """
        # Use markdown library
        try:
            import markdown as md_lib
            html = md_lib.markdown(
                markdown,
                extensions=['tables', 'fenced_code', 'codehilite', 'toc']
            )
        except ImportError:
            # Fallback to basic conversion
            html = self._basic_convert(markdown)

        # Apply CSS if provided
        css_path = options.get('css_path', self.css_path)
        if css_path:
            html = self._inject_css(html, css_path)

        # Apply template if provided
        template_path = options.get('template')
        if template_path:
            html = self._apply_template(html, template_path, options)

        return html

    def _basic_convert(self, markdown: str) -> str:
        """Basic markdown to HTML conversion (fallback)."""
        html = markdown

        # Headers
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)

        # Bold
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

        # Italic
        html = re.sub(r'_(.+?)_', r'<em>\1</em>', html)

        # Links
        html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)

        # Lists
        html = re.sub(r'^\s*[-*+]\s+(.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)

        # Paragraphs
        paragraphs = html.split('\n\n')
        html = '\n'.join(f'<p>{p}</p>' if not p.startswith('<') else p for p in paragraphs)

        return html

    def _inject_css(self, html: str, css_path: str) -> str:
        """Inject CSS into HTML."""
        css_file = Path(css_path)
        if css_file.exists():
            css_content = css_file.read_text(encoding='utf-8')
            css_link = f'<style>\n{css_content}\n</style>'
            if '<head>' in html:
                html = html.replace('</head>', f'{css_link}\n</head>')
            else:
                html = f'<head>{css_link}</head>\n{html}'
        return html

    def _apply_template(self, html: str, template_path: str, options: dict) -> str:
        """Apply HTML template."""
        try:
            from jinja2 import Template
            template_file = Path(template_path)
            if template_file.exists():
                template_content = template_file.read_text(encoding='utf-8')
                template = Template(template_content)
                return template.render(content=html, **options)
        except ImportError:
            pass
        return html

