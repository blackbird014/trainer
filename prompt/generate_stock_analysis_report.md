# Generate Stock Analysis Report from JSON

## Prompt Template

When provided with a JSON file containing stock financial data (e.g., `stock_data_YYYYMMDD_HHMMSS.json`), generate a comprehensive markdown analysis report following this structure:

## Instructions

1. **Read the JSON file** containing an array of stock ticker data
2. **Transform the data** into a well-formatted markdown report with the structure below
3. **Preserve the original JSON file** - do not modify or delete it
4. **Create a new markdown file** named `stock_analysis_report.md` (or with timestamp if multiple reports exist)

## Report Structure

### 1. Header Section
- Title: "Stock Analysis Report"
- Generated date
- List of tickers analyzed

### 2. Summary Dashboard
Create a quick overview table with key metrics:

| Ticker | Market Cap | Forward P/E | Trailing P/E | Revenue (TTM) | Profit Margin | ROE | Quarterly Rev Growth |
|--------|------------|-------------|--------------|---------------|---------------|-----|---------------------|
| [Ticker] | [Value] | [Value] | [Value] | [Value] | [Value] | [Value] | [Value] |

Include a "Quick Insights" section highlighting:
- Largest market cap
- Best profit margin
- Highest growth
- Most profitable
- Best value (lowest Forward P/E)

### 3. Individual Company Profiles

For each ticker in the JSON array, create a detailed section:

#### [TICKER] - [Company Name]

**Extracted:** [ISO timestamp from JSON]

##### Valuation Metrics
| Metric | Value |
|--------|-------|
| Market Cap | [value] |
| Enterprise Value | [value] |
| Trailing P/E | [value] |
| Forward P/E | [value] |
| Price/Sales | [value] |
| Price/Book | [value] |
| EV/Revenue | [value] |
| EV/EBITDA | [value] |

##### Financial Metrics
| Metric | Value |
|--------|-------|
| Revenue (TTM) | [value] |
| Revenue Per Share | [value] |
| Quarterly Revenue Growth (YoY) | [value] |
| Gross Profit | [value] |
| EBITDA | [value] |
| Net Income | [value] |
| Earnings Per Share | [value] |
| Quarterly Earnings Growth (YoY) | [value] |

##### Profitability Metrics
| Metric | Value |
|--------|-------|
| Profit Margin | [value] |
| Operating Margin | [value] |
| Return on Assets (ROA) | [value] |
| Return on Equity (ROE) | [value] |

**Note:** Add any relevant notes for companies with unusual metrics (e.g., pre-profit companies, negative values, missing data)

---

### 4. Comparison Tables

Create side-by-side comparison tables for easy analysis:

#### Valuation Comparison
| Metric | [Ticker1] | [Ticker2] | [Ticker3] | ... |
|--------|-----------|-----------|-----------|-----|
| Market Cap | [value] | [value] | [value] | ... |
| Enterprise Value | [value] | [value] | [value] | ... |
| Trailing P/E | [value] | [value] | [value] | ... |
| Forward P/E | [value] | [value] | [value] | ... |
| Price/Sales | [value] | [value] | [value] | ... |
| Price/Book | [value] | [value] | [value] | ... |
| EV/Revenue | [value] | [value] | [value] | ... |
| EV/EBITDA | [value] | [value] | [value] | ... |

#### Financial Performance Comparison
| Metric | [Ticker1] | [Ticker2] | [Ticker3] | ... |
|--------|-----------|-----------|-----------|-----|
| Revenue (TTM) | [value] | [value] | [value] | ... |
| Revenue Per Share | [value] | [value] | [value] | ... |
| Quarterly Rev Growth | [value] | [value] | [value] | ... |
| Gross Profit | [value] | [value] | [value] | ... |
| EBITDA | [value] | [value] | [value] | ... |
| Net Income | [value] | [value] | [value] | ... |
| Earnings Per Share | [value] | [value] | [value] | ... |
| Quarterly Earnings Growth | [value] | [value] | [value] | ... |

#### Profitability Comparison
| Metric | [Ticker1] | [Ticker2] | [Ticker3] | ... |
|--------|-----------|-----------|-----------|-----|
| Profit Margin | [value] | [value] | [value] | ... |
| Operating Margin | [value] | [value] | [value] | ... |
| Return on Assets (ROA) | [value] | [value] | [value] | ... |
| Return on Equity (ROE) | [value] | [value] | [value] | ... |

### 5. Analysis Notes Section

Include a section with:
- Key observations
- Market leaders identification
- Growth companies highlights
- Valuation insights
- Profitability leaders

### 6. Data Source Footer

- Source: Yahoo Finance (or appropriate source)
- Extraction date
- Reference to original JSON file

---

## JSON Structure Expected

The JSON file should follow this structure:

```json
[
  {
    "ticker": "TICKER",
    "extractedAt": "ISO_TIMESTAMP",
    "valuation": {
      "marketCap": "...",
      "enterpriseValue": "...",
      "trailingPE": "...",
      "forwardPE": "...",
      "pegRatio": "...",
      "priceToSales": "...",
      "priceToBook": "...",
      "enterpriseValueRevenue": "...",
      "enterpriseValueEBITDA": "..."
    },
    "financials": {
      "revenue": "...",
      "revenuePerShare": "...",
      "quarterlyRevenueGrowth": "...",
      "grossProfit": "...",
      "ebitda": "...",
      "netIncome": "...",
      "earningsPerShare": "...",
      "quarterlyEarningsGrowth": "..."
    },
    "profitability": {
      "profitMargin": "...",
      "operatingMargin": "...",
      "returnOnAssets": "...",
      "returnOnEquity": "..."
    }
  }
]
```

## Usage Example

**Input:**
```
Read stock_data_20251119_134901.json and generate a stock analysis report 
following the template in generate_stock_analysis_report.md
```

**Output:**
- A new markdown file: `stock_analysis_report.md` with all sections formatted
- Original JSON file preserved

## Formatting Guidelines

1. **Tables:** Use proper markdown table syntax with aligned columns
2. **Headers:** Use appropriate heading levels (## for sections, ### for subsections, #### for sub-subsections)
3. **Emojis:** Use emojis sparingly for visual enhancement (📊, 📈, 🔄, 📝, 📄)
4. **Values:** Preserve original formatting from JSON (e.g., "3.95T", "52.41%", "--")
5. **Missing Data:** Handle missing/null values gracefully (show "--" or "N/A")
6. **Negative Values:** Preserve negative values as-is (e.g., "-407.92M")
7. **Large Numbers:** Keep original formatting (B for billions, T for trillions, M for millions)

## Special Cases

- **Pre-profit companies:** Add notes explaining negative metrics
- **Missing P/E ratios:** Use "--" and note why (e.g., negative earnings)
- **Extreme values:** Highlight in insights section (e.g., very high Price/Sales ratios)
- **Growth companies:** Distinguish between mature and growth-stage companies

## Output File Naming

- Default: `stock_analysis_report.md`
- If multiple reports exist: `stock_analysis_report_YYYYMMDD.md`
- Include timestamp in header, not filename (unless multiple reports needed)

---

## Quick Reference

**To generate a report:**
1. Provide the JSON file path
2. Reference this prompt template
3. Request: "Generate stock analysis report from [JSON_FILE] using the template in generate_stock_analysis_report.md"

**The AI will:**
- Read the JSON file
- Transform data into markdown tables
- Create comprehensive report with all sections
- Preserve original JSON file
- Generate new markdown report file

