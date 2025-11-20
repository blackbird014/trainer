# Stock Data Scraper - Yahoo Finance

## Overview

This project uses Cursor's built-in browser automation tools to scrape financial data from Yahoo Finance. No Python scripts needed - just describe what you want and I'll use the browser tools to extract the data.

## Quick Start

### Single Company
```
Scrape financial data for NVDA from Yahoo Finance
```

### Multiple Companies
```
Scrape financial data for NVDA, AAPL, MU, TSLA, MSFT from Yahoo Finance
```

## How It Works

1. **You provide ticker symbols** (e.g., NVDA, AAPL, MU)
2. **I navigate** to each ticker's Yahoo Finance statistics page
3. **I extract** all financial metrics from the tables
4. **I format** the data into structured JSON
5. **I save** the results to a file for your analysis

## Project Structure

```
trainer/
├── prompt/              # Reusable prompt templates
│   ├── scrape_tickers.md
│   └── generate_stock_analysis_report.md
├── output/              # Generated files (build directory)
│   ├── json/           # JSON data files
│   ├── report/         # Markdown reports
│   ├── pdf/            # PDF reports (to be generated)
│   └── html/           # HTML reports (to be generated)
└── [documentation files]
```

## Files

- `prompt/scrape_tickers.md` - Template for batch scraping requests
- `prompt/generate_stock_analysis_report.md` - Template for generating analysis reports
- `YAHOO_FINANCE_SCRAPING_INSTRUCTIONS.md` - Detailed scraping instructions
- `SCRAPING_GUIDE.md` - General browser automation guide

## Data Extracted

### Valuation Metrics
- Market Cap
- Enterprise Value
- Trailing P/E
- Forward P/E
- PEG Ratio
- Price/Sales
- Price/Book
- Enterprise Value/Revenue
- Enterprise Value/EBITDA

### Financial Metrics
- Revenue (TTM)
- Revenue Per Share
- Quarterly Revenue Growth (YoY)
- Gross Profit
- EBITDA
- Net Income
- Earnings Per Share
- Quarterly Earnings Growth (YoY)

### Profitability Metrics
- Profit Margin
- Operating Margin
- Return on Assets (ROA)
- Return on Equity (ROE)

## Output Format

Data is saved as a JSON array, with one object per ticker:

```json
[
  {
    "ticker": "NVDA",
    "extractedAt": "2025-11-19T13:46:51.150Z",
    "valuation": { ... },
    "financials": { ... },
    "profitability": { ... }
  },
  {
    "ticker": "AAPL",
    ...
  }
]
```

## Usage Example

**Request:**
```
Scrape these tickers: NVDA, AAPL, MU, TSLA
Extract Forward P/E, Trailing P/E, Revenue, and all profitability metrics.
Save to stock_data.json
```

**Result:**
A JSON file with comprehensive financial data for all requested tickers, ready for analysis.

## Next Steps

After scraping, you can:
1. Use the JSON data for company analysis
2. Compare metrics across companies
3. Feed the data into your analysis prompts
4. Create visualizations or reports

## Advantages Over Python Scripts

✅ **No code needed** - Just describe what you want  
✅ **Visual understanding** - I can see page structure  
✅ **Handles dynamic content** - Waits for pages to load  
✅ **Built-in tools** - No Selenium/Playwright setup  
✅ **Smart extraction** - Understands page structure automatically  

