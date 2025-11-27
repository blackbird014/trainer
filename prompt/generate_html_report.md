# Generate HTML Report from Markdown

## Prompt Template

When provided with a markdown stock analysis report from `output/report/` directory (e.g., `output/report/stock_analysis_report.md`), generate a professional HTML version and save it to `output/html/` directory.

## Instructions

1. **Read the markdown report** file from `output/report/` directory
2. **Manually convert to HTML** - DO NOT use command-line tools (wc, pandoc, etc.)
3. **Parse the structure** manually:
   - Headers (h1, h2, h3, h4)
   - Tables (convert markdown tables to HTML `<table>` elements)
   - Lists (ul, ol)
   - Code blocks (pre, code)
   - Bold/italic text (strong, em)
   - Horizontal rules (hr)
4. **Apply CSS classes** from `report.css`:
   - Use `.positive` class for positive/good values (green)
   - Use `.negative` class for negative/bad values (red)
   - Use `.insights` class for highlighted insights sections
   - Use `.note` class for important notes
   - Use `.company-section` for distinct company sections
5. **Color code values**:
   - Positive metrics (revenue growth, profit margins, etc.) → class="positive"
   - Negative metrics (losses, declines, etc.) → class="negative"
6. **Format tables properly**:
   - Use `<table>`, `<thead>`, `<tbody>`, `<tr>`, `<th>`, `<td>` elements
   - Apply proper table structure with headers
7. **Save to** `output/html/[same_filename].html` (e.g., `stock_analysis_report.md` → `stock_analysis_report.html`)
8. **Add navigation link** at the top: "← Back to Index" linking to `../../index.html`
9. **Do NOT** create or modify `index.html` in root (that's handled separately)

## CRITICAL: Manual Conversion Requirements

**DO NOT use command-line tools** (wc, pandoc, grep, etc.) for conversion. You must:
- Read the entire markdown file
- Manually parse each section
- Convert markdown syntax to HTML elements
- Apply appropriate CSS classes
- Format tables with proper HTML table structure
- Add color coding using `.positive` and `.negative` classes

## HTML Structure Requirements

### 1. HTML5 Document Structure
- Proper DOCTYPE and meta tags
- Responsive viewport meta tag
- Semantic HTML5 elements

### 2. CSS Styling
**Link to external stylesheet** instead of embedding CSS:
- Use: `<link rel="stylesheet" href="../css/report.css">`
- The CSS file is located at: `output/css/report.css`
- From `output/html/` directory, the relative path is: `../css/report.css`
- Both HTML and CSS are in the `output/` directory, so only one level up (`../`)
- The shared stylesheet includes:
  - Modern, clean design
  - Responsive layout (mobile-friendly)
  - Professional color scheme
  - Styled tables with hover effects
  - Color coding for positive/negative values:
    - Green for positive metrics
    - Red for negative metrics
  - Print-friendly styles

### 3. Key Features
- **Navigation:** "← Back to Index" link at the top (links to `../../index.html`)
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
    <link rel="stylesheet" href="../css/report.css">
</head>
<body>
    <div class="container">
        <div class="back-link">
            <a href="../../index.html">← Back to Index</a>
        </div>
        <h1>Stock Analysis Report</h1>
        <!-- Content sections -->
    </div>
</body>
</html>
```

**Important Paths:**
- **CSS:** `../css/report.css` (from `output/html/` to `output/css/report.css`)
- **Back link:** `../../index.html` (from `output/html/` to root `index.html`)
- Path breakdown:
  - CSS: `../` (up to output) → `css/report.css`
  - Index: `../` (up to output) → `../` (up to root) → `index.html`

## How to Use This Prompt

**You must specify which markdown file to convert:**

**Example 1 - Specific file:**
```
Read output/report/stock_analysis_report.md and generate an HTML version 
following the template in prompt/generate_html_report.md
```

**Example 2 - With explicit instruction:**
```
Generate HTML from output/report/stock_analysis_report.md using 
prompt/generate_html_report.md
```

**Example 3 - Simple:**
```
Convert output/report/stock_analysis_report.md to HTML
```

**Output:**
- `output/html/stock_analysis_report.html` - Full HTML report with back link to index

**Note:** 
- Always specify the markdown file path (e.g., `output/report/stock_analysis_report.md`)
- The HTML will be saved with the same filename (`.md` → `.html`) in `output/html/`
- The `index.html` in root should be updated separately using the `generate_index_page.md` prompt to add a link to this new report

## File Paths

- **Input:** Markdown files in `output/report/*.md`
- **Output:** HTML files in `output/html/*.html`
- **CSS:** Shared stylesheet at `output/css/report.css`
- **Index:** Landing page at `index.html` (root directory)

## GitHub Pages Setup

After generating HTML:
1. Ensure `index.html` exists in project root (with links to reports)
2. Go to repository Settings → Pages
3. Select source: "Deploy from a branch"
4. Select branch: `main`
5. Select folder: `/ (root)`
6. Save

The site will be available at: `https://[username].github.io/trainer/`

## Notes

- **Use external CSS:** Link to `../css/report.css` instead of embedding styles
- **Shared stylesheet:** All HTML reports use the same CSS file for consistency
- **Easy maintenance:** Update CSS once, affects all reports
- Ensure tables are responsive for mobile devices
- Use semantic HTML for accessibility
- Include proper meta tags for SEO
- Test in multiple browsers

