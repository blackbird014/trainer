# Stock Ticker Scraping Template

## Instructions for AI Assistant

When I provide a list of stock tickers, please:

1. **For each ticker**, navigate to: `https://finance.yahoo.com/quote/{TICKER}/key-statistics/`
2. **Wait 2-3 seconds** for the page to load
3. **Extract** the following metrics from the statistics tables:
   - Forward P/E
   - Trailing P/E  
   - Revenue (TTM)
   - Market Cap
   - Enterprise Value
   - PEG Ratio
   - Price/Sales
   - Price/Book
   - EBITDA
   - Profit Margin
   - Operating Margin
   - Return on Assets (ROA)
   - Return on Equity (ROE)
   - Quarterly Revenue Growth (YoY)
   - Quarterly Earnings Growth (YoY)
   - Earnings Per Share (EPS)

4. **Format** each ticker's data as a JSON object following this structure:
```json
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
```

5. **Combine** all tickers into a single JSON array
6. **Save** the result to a file named `stock_data_{timestamp}.json`

## Example Usage

**Input:**
```
Scrape these tickers: NVDA, AAPL, MU, TSLA, MSFT, GOOGL, META, AMD
```

**Output:**
A file `stock_data_YYYYMMDD_HHMMSS.json` containing an array of all ticker data.

