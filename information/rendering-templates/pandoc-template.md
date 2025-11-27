# Pandoc PDF Generation Template

## Basic Usage

### Single Markdown File
```bash
cd [project-directory] && pandoc document.md -o output.pdf --pdf-engine=xelatex -V geometry:margin=1in -V fontsize=11pt -V documentclass=report --toc
```

### Multiple Markdown Files
```bash
cd [project-directory] && pandoc file1.md file2.md file3.md -o combined-output.pdf --pdf-engine=xelatex -V geometry:margin=1in -V fontsize=11pt -V documentclass=report --toc
```

## Standard Options

- `--pdf-engine=xelatex`: Uses XeLaTeX engine for better Unicode support
- `-V geometry:margin=1in`: Sets 1 inch margins on all sides
- `-V fontsize=11pt`: Sets document font size to 11pt
- `-V documentclass=report`: Uses LaTeX report class (good for longer documents)
- `--toc`: Generates table of contents automatically

## Usage Notes

- **File Order**: Documents are merged in the order specified
- **Output Naming**: Use descriptive filenames (e.g., `analysis-complete.pdf`)
- **Emoji Support**: Emoji warnings are cosmetic and don't affect PDF rendering
- **Table of Contents**: Automatically generated with `--toc` flag
- **Path Handling**: Use relative paths from your project directory

## Examples

### Research Report
```bash
pandoc introduction.md methodology.md results.md conclusion.md -o research-report.pdf --pdf-engine=xelatex -V geometry:margin=1in -V fontsize=11pt -V documentclass=report --toc
```

### Analysis Collection
```bash
pandoc overview.md company1-analysis.md company2-analysis.md summary.md -o company-analyses.pdf --pdf-engine=xelatex -V geometry:margin=1in -V fontsize=11pt -V documentclass=report --toc
```

