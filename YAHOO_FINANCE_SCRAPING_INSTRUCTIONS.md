# Yahoo Finance Scraping Instructions

## Overview
This document provides instructions for scraping financial data from Yahoo Finance using Cursor's browser automation tools.

## Target Metrics
Extract the following financial metrics for each ticker:
- **Forward P/E** (Price-to-Earnings forward)
- **Trailing P/E** (Price-to-Earnings trailing)
- **Revenue/Sales** (TTM - Trailing Twelve Months)
- **Market Cap**
- **Enterprise Value**
- **PEG Ratio**
- **Price/Sales**
- **Price/Book**
- **EBITDA**
- **Profit Margin**
- **Operating Margin**
- **Return on Assets (ROA)**
- **Return on Equity (ROE)**
- **Quarterly Revenue Growth (YoY)**
- **Quarterly Earnings Growth (YoY)**
- **Earnings Per Share (EPS)**

## Scraping Process

### Step 1: Navigate to Stock Quote Page
Navigate to: `https://finance.yahoo.com/quote/{TICKER}/`

Example: `https://finance.yahoo.com/quote/NVDA/`

### Step 2: Navigate to Statistics Page
From the quote page, navigate to the Statistics page:
`https://finance.yahoo.com/quote/{TICKER}/key-statistics/`

Example: `https://finance.yahoo.com/quote/NVDA/key-statistics/`

### Step 3: Wait for Page Load
Wait 2-3 seconds for the page to fully load all dynamic content.

### Step 4: Extract Data
Use JavaScript evaluation to extract data from tables on the statistics page. The data is typically in `<table>` elements with `<tr>` rows containing `<td>` cells.

### Step 5: Structure Output
Format the extracted data into a standardized JSON structure (see format below).

## JSON Output Format

```json
{
  "ticker": "NVDA",
  "extractedAt": "2025-11-19T13:46:51.150Z",
  "valuation": {
    "marketCap": "4.42T",
    "enterpriseValue": "4.37T",
    "trailingPE": "51.67",
    "forwardPE": "26.95",
    "pegRatio": "0.78",
    "priceToSales": "27.06",
    "priceToBook": "44.10",
    "enterpriseValueRevenue": "26.46",
    "enterpriseValueEBITDA": "42.37"
  },
  "financials": {
    "revenue": "165.22B",
    "revenuePerShare": "6.76",
    "quarterlyRevenueGrowth": "55.60%",
    "grossProfit": "115.4B",
    "ebitda": "98.28B",
    "netIncome": "86.6B",
    "earningsPerShare": "3.52",
    "quarterlyEarningsGrowth": "59.20%"
  },
  "profitability": {
    "profitMargin": "52.41%",
    "operatingMargin": "60.84%",
    "returnOnAssets": "53.09%",
    "returnOnEquity": "109.42%"
  }
}
```

## Usage Instructions

### Single Ticker
Simply ask: "Scrape financial data for NVDA from Yahoo Finance"

### Multiple Tickers
Provide a list of tickers: "Scrape financial data for NVDA, AAPL, MU, TSLA from Yahoo Finance"

I will:
1. Process each ticker sequentially
2. Extract all metrics from the statistics page
3. Combine into a single JSON array
4. Save to a file for your analysis

## Example Request

**Input:**
```
Scrape financial data for the following tickers: NVDA, AAPL, MU, TSLA, MSFT
Extract Forward P/E, Trailing P/E, Revenue, Market Cap, and all profitability metrics.
Output as a JSON array with one object per ticker.
```

**Expected Output:**
A JSON file containing an array of company data objects, each following the format above.

## Notes

- Yahoo Finance may rate-limit requests, so processing multiple tickers may take time
- Some metrics may be "N/A" for certain companies - these will be excluded from output
- The statistics page contains the most comprehensive data
- Data is extracted from HTML tables, so the structure may change if Yahoo updates their site

