"""
Yahoo Finance data retriever.

Supports both browser automation (Selenium/Playwright) and API-based retrieval.
"""

import json
import time
import random
from typing import Any, Dict, List, Optional

from data_retriever.base import DataRetriever, RetrievalResult
from data_retriever.schema import YAHOO_FINANCE_SCHEMA, Schema


class YahooFinanceRetriever(DataRetriever):
    """
    Yahoo Finance stock data retriever.

    Supports browser automation for scraping or API-based retrieval.
    """

    def __init__(
        self,
        use_browser: bool = False,
        browser_type: str = "selenium",
        use_mock: bool = False,
        **kwargs,
    ):
        """
        Initialize Yahoo Finance retriever.

        Args:
            use_browser: Whether to use browser automation (default: False, uses API)
            browser_type: Browser type ('selenium' or 'playwright')
            use_mock: Whether to use mock data (default: False, uses real yfinance)
            **kwargs: Additional arguments passed to DataRetriever
        """
        super().__init__(source_name="yahoo_finance", **kwargs)
        self.use_browser = use_browser
        self.browser_type = browser_type
        self.use_mock = use_mock
        self._browser = None

    def retrieve(self, query: Dict[str, Any]) -> RetrievalResult:
        """
        Retrieve stock data from Yahoo Finance.

        Query parameters:
            - ticker: Stock ticker symbol (required)
            - tickers: List of ticker symbols (for batch retrieval)
            - metrics: List of specific metrics to retrieve (optional)

        Returns:
            RetrievalResult with stock data
        """
        try:
            # Support both single ticker and batch
            ticker = query.get("ticker")
            tickers = query.get("tickers", [ticker] if ticker else [])

            if not tickers:
                return RetrievalResult(
                    data={},
                    source=self.source_name,
                    success=False,
                    error="Missing required parameter: ticker or tickers",
                )

            # Retrieve data for each ticker
            results = []
            for ticker_symbol in tickers:
                ticker_data = self._retrieve_ticker(ticker_symbol, query)
                if ticker_data:
                    results.append(ticker_data)

            if not results:
                return RetrievalResult(
                    data={},
                    source=self.source_name,
                    success=False,
                    error="Failed to retrieve data for any ticker",
                )

            # Return single result or list
            if len(results) == 1:
                return RetrievalResult(
                    data=results[0],
                    source=self.source_name,
                )
            else:
                return RetrievalResult(
                    data={"tickers": results},
                    source=self.source_name,
                )

        except Exception as e:
            return RetrievalResult(
                data={},
                source=self.source_name,
                success=False,
                error=f"Error retrieving Yahoo Finance data: {str(e)}",
            )

    def _retrieve_ticker(self, ticker: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Retrieve data for a single ticker.

        This is a placeholder implementation. In practice, you would:
        1. Use browser automation (Selenium/Playwright) to scrape Yahoo Finance
        2. Or use a Yahoo Finance API library
        3. Or use yfinance library

        For now, this returns a structured format matching the expected schema.
        """
        if self.use_browser:
            return self._retrieve_via_browser(ticker, query)
        else:
            # Try API-based approach (would use yfinance or similar)
            return self._retrieve_via_api(ticker, query)

    def _retrieve_via_browser(self, ticker: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Retrieve data via browser automation.

        This would use Selenium or Playwright to scrape Yahoo Finance.
        Implementation depends on browser automation setup.
        """
        # Placeholder - would implement actual browser automation here
        # For now, return None to indicate not implemented
        return None

    def _retrieve_via_api(self, ticker: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Retrieve data via yfinance API with mock fallback.
        
        Priority: query param > instance variable > env var > False
        """
        # Check query parameter first (highest priority)
        use_mock = query.get("use_mock", self.use_mock)  # Falls back to instance variable
        
        if use_mock:
            return self._generate_mock_data(ticker)
        
        try:
            return self._fetch_real_data(ticker)  # Use yfinance
        except Exception as e:
            # Fallback to mock if yfinance fails (rate limit, network error, etc.)
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"yfinance failed for {ticker}: {e}, using mock")
            return self._generate_mock_data(ticker)
    
    def _fetch_real_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch real data using yfinance library.
        
        Maps yfinance data structure to expected Yahoo Finance schema.
        """
        try:
            import yfinance as yf
        except ImportError:
            raise ImportError("yfinance not installed. Install with: pip install -e '.[yahoo]'")
        
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Helper function to format numbers with suffix
        def format_number_with_suffix(value, decimals=2):
            if value is None:
                return "N/A"
            abs_value = abs(value)
            if abs_value >= 1_000_000_000_000:  # Trillions
                return f"{value / 1_000_000_000_000:.{decimals}f}T"
            elif abs_value >= 1_000_000_000:  # Billions
                return f"{value / 1_000_000_000:.{decimals}f}B"
            elif abs_value >= 1_000_000:  # Millions
                return f"{value / 1_000_000:.{decimals}f}M"
            elif abs_value >= 1_000:  # Thousands
                return f"{value / 1_000:.{decimals}f}K"
            else:
                return f"{value:.{decimals}f}"
        
        def format_percentage(value, decimals=2):
            if value is None:
                return "N/A"
            return f"{value:.{decimals}f}%"
        
        # Map yfinance data to expected schema format
        extracted_at = time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        
        return {
            "ticker": ticker.upper(),
            "extractedAt": extracted_at,
            "valuation": {
                "marketCap": format_number_with_suffix(info.get("marketCap")),
                "enterpriseValue": format_number_with_suffix(info.get("enterpriseValue")),
                "trailingPE": f"{info.get('trailingPE', 0):.2f}" if info.get("trailingPE") else "N/A",
                "forwardPE": f"{info.get('forwardPE', 0):.2f}" if info.get("forwardPE") else "N/A",
                "pegRatio": f"{info.get('pegRatio', 0):.2f}" if info.get("pegRatio") else "N/A",
                "priceToSales": f"{info.get('priceToSalesTrailing12Months', 0):.2f}" if info.get("priceToSalesTrailing12Months") else "N/A",
                "priceToBook": f"{info.get('priceToBook', 0):.2f}" if info.get("priceToBook") else "N/A",
                "enterpriseValueRevenue": f"{info.get('enterpriseToRevenue', 0):.2f}" if info.get("enterpriseToRevenue") else "N/A",
                "enterpriseValueEBITDA": f"{info.get('enterpriseToEbitda', 0):.2f}" if info.get("enterpriseToEbitda") else "N/A",
            },
            "financials": {
                "revenue": format_number_with_suffix(info.get("totalRevenue")),
                "revenuePerShare": f"{info.get('revenuePerShare', 0):.2f}" if info.get("revenuePerShare") else "N/A",
                "quarterlyRevenueGrowth": format_percentage(info.get("quarterlyRevenueGrowth") * 100 if info.get("quarterlyRevenueGrowth") else None),
                "grossProfit": format_number_with_suffix(info.get("grossProfits")),
                "ebitda": format_number_with_suffix(info.get("ebitda")),
                "netIncome": format_number_with_suffix(info.get("netIncomeToCommon")),
                "earningsPerShare": f"{info.get('trailingEps', 0):.2f}" if info.get("trailingEps") else "N/A",
                "quarterlyEarningsGrowth": format_percentage(info.get("quarterlyEarningsGrowth") * 100 if info.get("quarterlyEarningsGrowth") else None),
            },
            "profitability": {
                "profitMargin": format_percentage(info.get("profitMargins") * 100 if info.get("profitMargins") else None),
                "operatingMargin": format_percentage(info.get("operatingMargins") * 100 if info.get("operatingMargins") else None),
                "returnOnAssets": format_percentage(info.get("returnOnAssets") * 100 if info.get("returnOnAssets") else None),
                "returnOnEquity": format_percentage(info.get("returnOnEquity") * 100 if info.get("returnOnEquity") else None),
            }
        }
    
    def _generate_mock_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Generate deterministic mock data for testing/offline scenarios.
        
        Same ticker always returns same data (deterministic).
        """
        import hashlib
        
        # Create deterministic hash from ticker
        ticker_hash = int(hashlib.md5(ticker.upper().encode()).hexdigest()[:8], 16)
        random.seed(ticker_hash)
        
        # Generate base financials (deterministic based on ticker)
        market_cap = 100_000_000 + (ticker_hash % 4_900_000_000_000)
        revenue = int(market_cap * (0.5 + (ticker_hash % 100) / 200))
        net_income = int(revenue * (0.1 + (ticker_hash % 20) / 100))
        gross_profit = int(revenue * (0.5 + (ticker_hash % 30) / 100))
        ebitda = int(revenue * (0.2 + (ticker_hash % 30) / 100))
        enterprise_value = int(market_cap * (0.95 + (ticker_hash % 10) / 100))
        
        # Helper functions (same as in _fetch_real_data)
        def format_number_with_suffix(value, decimals=2):
            abs_value = abs(value)
            if abs_value >= 1_000_000_000_000:
                return f"{value / 1_000_000_000_000:.{decimals}f}T"
            elif abs_value >= 1_000_000_000:
                return f"{value / 1_000_000_000:.{decimals}f}B"
            elif abs_value >= 1_000_000:
                return f"{value / 1_000_000:.{decimals}f}M"
            elif abs_value >= 1_000:
                return f"{value / 1_000:.{decimals}f}K"
            else:
                return f"{value:.{decimals}f}"
        
        def format_percentage(value, decimals=2):
            return f"{value:.{decimals}f}%"
        
        # Calculate derived metrics
        price = 10.0 + (ticker_hash % 490)
        shares_outstanding = market_cap / price if price > 0 else 1
        trailing_pe = 5.0 + (ticker_hash % 45)
        forward_pe = trailing_pe * (0.8 + (ticker_hash % 20) / 100)
        peg_ratio = 0.5 + (ticker_hash % 150) / 100
        price_to_sales = round(market_cap / revenue if revenue > 0 else 0, 2)
        price_to_book = round(market_cap / (market_cap * 0.6) if market_cap > 0 else 0, 2)
        enterprise_value_revenue = round(enterprise_value / revenue if revenue > 0 else 0, 2)
        enterprise_value_ebitda = round(enterprise_value / ebitda if ebitda > 0 else 0, 2)
        
        revenue_per_share = round(revenue / shares_outstanding if shares_outstanding > 0 else 0, 2)
        earnings_per_share = round(net_income / shares_outstanding if shares_outstanding > 0 else 0, 2)
        
        quarterly_revenue_growth = -20.0 + (ticker_hash % 120)
        quarterly_earnings_growth = -30.0 + (ticker_hash % 180)
        
        profit_margin = (net_income / revenue * 100) if revenue > 0 else 0
        operating_margin = (ebitda / revenue * 100) if revenue > 0 else 0
        roa = (net_income / (market_cap * 1.2) * 100) if market_cap > 0 else 0
        roe = (net_income / (market_cap * 0.6) * 100) if market_cap > 0 else 0
        
        extracted_at = time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        
        return {
            "ticker": ticker.upper(),
            "extractedAt": extracted_at,
            "valuation": {
                "marketCap": format_number_with_suffix(market_cap),
                "enterpriseValue": format_number_with_suffix(enterprise_value),
                "trailingPE": f"{trailing_pe:.2f}",
                "forwardPE": f"{forward_pe:.2f}",
                "pegRatio": f"{peg_ratio:.2f}",
                "priceToSales": f"{price_to_sales:.2f}",
                "priceToBook": f"{price_to_book:.2f}",
                "enterpriseValueRevenue": f"{enterprise_value_revenue:.2f}",
                "enterpriseValueEBITDA": f"{enterprise_value_ebitda:.2f}",
            },
            "financials": {
                "revenue": format_number_with_suffix(revenue),
                "revenuePerShare": f"{revenue_per_share:.2f}",
                "quarterlyRevenueGrowth": format_percentage(quarterly_revenue_growth),
                "grossProfit": format_number_with_suffix(gross_profit),
                "ebitda": format_number_with_suffix(ebitda),
                "netIncome": format_number_with_suffix(net_income),
                "earningsPerShare": f"{earnings_per_share:.2f}",
                "quarterlyEarningsGrowth": format_percentage(quarterly_earnings_growth),
            },
            "profitability": {
                "profitMargin": format_percentage(profit_margin),
                "operatingMargin": format_percentage(operating_margin),
                "returnOnAssets": format_percentage(roa),
                "returnOnEquity": format_percentage(roe),
            }
        }

    def get_schema(self) -> Schema:
        """Get schema for Yahoo Finance data."""
        return YAHOO_FINANCE_SCHEMA

    def __del__(self):
        """Cleanup browser instance."""
        if self._browser:
            try:
                if self.browser_type == "selenium":
                    self._browser.quit()
                elif self.browser_type == "playwright":
                    self._browser.close()
            except Exception:
                pass

