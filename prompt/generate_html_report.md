# Generate HTML Report from Markdown

## Prompt Template

When provided with a markdown stock analysis report (e.g., `output/report/stock_analysis_report.md`), generate a professional HTML version suitable for GitHub Pages deployment.

## Instructions

1. **Read the markdown report** file
2. **Convert to HTML** with professional styling
3. **Save to** `output/html/stock_analysis_report.html`
4. **Also create** `index.html` in project root for GitHub Pages

## HTML Structure Requirements

### 1. HTML5 Document Structure
- Proper DOCTYPE and meta tags
- Responsive viewport meta tag
- Semantic HTML5 elements

### 2. CSS Styling
Include embedded CSS with:
- Modern, clean design
- Responsive layout (mobile-friendly)
- Professional color scheme
- Styled tables with hover effects
- Color coding for positive/negative values:
  - Green for positive metrics
  - Red for negative metrics
- Print-friendly styles

### 3. Key Features
- **Tables:** Well-formatted, responsive tables
- **Color coding:** Positive values in green, negative in red
- **Company sections:** Distinct sections for each company
- **Insights box:** Highlighted insights section
- **Notes:** Styled note boxes for important information
- **Footer:** Data source and disclaimer

### 4. Content Sections
Convert all markdown sections:
- Header with title and metadata
- Summary Dashboard table
- Quick Insights box
- Individual Company Profiles (each in a styled section)
- Comparison Tables
- Analysis Notes
- Footer with data source

## Styling Guidelines

### Colors
- Primary: #3498db (blue)
- Success: #27ae60 (green)
- Danger: #e74c3c (red)
- Warning: #ffc107 (yellow)
- Text: #333 (dark gray)
- Background: #f5f5f5 (light gray)

### Typography
- Font: System font stack (-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, etc.)
- Headings: Bold, colored appropriately
- Tables: Clear borders, alternating row colors on hover

### Layout
- Max-width container: 1200px
- Padding: 40px (20px on mobile)
- Rounded corners: 8px
- Box shadows for depth

## Example HTML Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Analysis Report</title>
    <style>
        /* Embedded CSS styles */
    </style>
</head>
<body>
    <div class="container">
        <h1>Stock Analysis Report</h1>
        <!-- Content sections -->
    </div>
</body>
</html>
```

## Usage Example

**Input:**
```
Read output/report/stock_analysis_report.md and generate an HTML version 
following the template in prompt/generate_html_report.md
```

**Output:**
- `output/html/stock_analysis_report.html` - Full HTML report
- `index.html` - Copy in project root for GitHub Pages

## GitHub Pages Setup

After generating HTML:
1. Ensure `index.html` exists in project root
2. Go to repository Settings → Pages
3. Select source: "Deploy from a branch"
4. Select branch: `main`
5. Select folder: `/ (root)`
6. Save

The site will be available at: `https://[username].github.io/trainer/`

## Notes

- Keep HTML self-contained (embedded CSS, no external dependencies)
- Ensure tables are responsive for mobile devices
- Use semantic HTML for accessibility
- Include proper meta tags for SEO
- Test in multiple browsers

