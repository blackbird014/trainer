# Generate Index Page for Reports

## Prompt Template

When HTML reports are generated in `output/html/`, create or update an `index.html` file in the project root that serves as a landing page listing all available reports.

## Instructions

1. **Scan** the `output/html/` directory for HTML report files
2. **Create/Update** `index.html` in project root
3. **List** all reports with metadata (date, tickers, etc.)
4. **Link** to each report file

## Index Page Structure

### Required Elements

1. **Header Section**
   - Title: "Stock Analysis Reports"
   - Subtitle/description
   - Brief explanation of what the site contains

2. **Reports Listing**
   - List of all available reports
   - Each report item should show:
     - Report title/name
     - Date generated
     - Tickers analyzed
     - Link to the HTML file

3. **Footer**
   - Data source information
   - Repository link
   - Disclaimer

### Design Guidelines

- **Modern, clean design** matching report styling
- **Responsive layout** for mobile devices
- **Hover effects** on report items
- **Clear visual hierarchy**
- **Professional color scheme**

## HTML Structure Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Analysis Reports</title>
    <style>
        /* Professional styling */
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Stock Analysis Reports</h1>
        <p class="subtitle">Financial data analysis and insights</p>
        
        <div class="description">
            <p>Brief description...</p>
        </div>
        
        <div class="reports-section">
            <h2>Available Reports</h2>
            <ul class="report-list">
                <li class="report-item">
                    <a href="output/html/[filename].html" class="report-link">
                        <div>
                            <div class="report-title">Report Title</div>
                            <div class="report-meta">Tickers • Generated: Date</div>
                        </div>
                        <span class="report-arrow">→</span>
                    </a>
                </li>
                <!-- More reports -->
            </ul>
        </div>
        
        <div class="footer">
            <!-- Footer content -->
        </div>
    </div>
</body>
</html>
```

## Report Metadata Extraction

For each HTML file in `output/html/`, extract:
- **Filename** (without extension for display)
- **Date** from the HTML content (look for "Generated:" or "Extraction Date")
- **Tickers** from the HTML content (look for "Tickers Analyzed:")

## Usage Example

**Input:**
```
Scan output/html/ directory and update index.html to list all available reports
```

**Output:**
- Updated `index.html` with links to all reports in `output/html/`

## Notes

- Index page should be **self-contained** (no external dependencies)
- Links should use **relative paths** (`output/html/filename.html`)
- Design should be **consistent** with report styling
- **Update** index.html whenever new reports are generated
- Keep it **simple** - no need for frameworks like Astro for this use case

## Alternative: Directory Listing

If you prefer, GitHub Pages can also show a directory listing by accessing:
- `https://username.github.io/trainer/output/html/`

But a custom index page provides better UX and branding.

