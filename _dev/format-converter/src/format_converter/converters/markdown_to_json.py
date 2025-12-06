"""
Markdown to JSON converter (heuristic-based).
"""

import re
from typing import Dict, Any, List, Optional


class MarkdownToJSONConverter:
    """Convert Markdown to JSON structure (heuristic-based)."""

    def convert(self, markdown: str, **options) -> Dict[str, Any]:
        """
        Convert markdown to JSON.

        Args:
            markdown: Markdown content
            **options: Additional options:
                - root_key: Root key name (default: "content")

        Returns:
            JSON dictionary
        """
        root_key = options.get('root_key', 'content')
        result = {root_key: {}}

        lines = markdown.split('\n')
        current_section = result[root_key]
        section_stack = [current_section]
        current_level = 0

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Skip empty lines
            if not line:
                i += 1
                continue

            # Check for headers
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if header_match:
                level = len(header_match.group(1))
                title = header_match.group(2).strip()

                # Adjust section stack based on level
                while len(section_stack) > level - current_level + 1:
                    section_stack.pop()

                # Create new section
                key = self._key_from_title(title)
                if key not in current_section:
                    current_section[key] = {}
                current_section = current_section[key]
                section_stack.append(current_section)
                current_level = level

                i += 1
                continue

            # Check for tables
            if '|' in line and line.count('|') >= 2:
                table_data = self._parse_table(lines, i)
                if table_data:
                    current_section['table'] = table_data
                    i = table_data.get('_end_line', i + 1)
                    continue

            # Check for lists
            if re.match(r'^\s*[-*+]\s+', line) or re.match(r'^\s*\d+\.\s+', line):
                list_data = self._parse_list(lines, i)
                if list_data:
                    current_section['list'] = list_data
                    i = list_data.get('_end_line', i + 1)
                    continue

            # Regular text
            if 'text' not in current_section:
                current_section['text'] = []
            current_section['text'].append(line)

            i += 1

        # Clean up helper keys
        self._cleanup(result[root_key])
        return result

    def _key_from_title(self, title: str) -> str:
        """Convert title to JSON key."""
        # Remove special characters, convert to snake_case
        key = re.sub(r'[^\w\s]', '', title.lower())
        key = re.sub(r'\s+', '_', key)
        return key or 'section'

    def _parse_table(self, lines: List[str], start_idx: int) -> Optional[Dict[str, Any]]:
        """Parse markdown table."""
        table_lines = []
        i = start_idx

        # Collect table lines
        while i < len(lines):
            line = lines[i].strip()
            if '|' in line and line.count('|') >= 2:
                table_lines.append(line)
                i += 1
            else:
                break

        if len(table_lines) < 2:  # Need header + separator
            return None

        # Parse header
        header = [cell.strip() for cell in table_lines[0].split('|')[1:-1]]

        # Parse rows
        rows = []
        for line in table_lines[2:]:  # Skip separator
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if len(cells) == len(header):
                row = {header[j]: cells[j] for j in range(len(header))}
                rows.append(row)

        return {
            'headers': header,
            'rows': rows,
            '_end_line': i
        }

    def _parse_list(self, lines: List[str], start_idx: int) -> Optional[List[str]]:
        """Parse markdown list."""
        items = []
        i = start_idx

        while i < len(lines):
            line = lines[i].strip()
            match = re.match(r'^\s*[-*+]\s+(.+)$', line) or re.match(r'^\s*\d+\.\s+(.+)$', line)
            if match:
                items.append(match.group(1))
                i += 1
            else:
                break

        if items:
            return {
                'items': items,
                '_end_line': i
            }
        return None

    def _cleanup(self, data: Dict[str, Any]):
        """Remove helper keys from data."""
        if isinstance(data, dict):
            keys_to_remove = [k for k in data.keys() if k.startswith('_')]
            for key in keys_to_remove:
                del data[key]
            for value in data.values():
                if isinstance(value, dict):
                    self._cleanup(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            self._cleanup(item)

