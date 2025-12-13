"""
Company data generator for seeding test data.

Generates fake company records matching the Yahoo Finance scraping format
from YAHOO_FINANCE_SCRAPING_INSTRUCTIONS.md and scrape_tickers.md.
This ensures seed_companies and scraped_metrics collections use the same format.
"""

import random
import string
from typing import List, Dict, Any
from datetime import datetime

# Sectors and industries for variety
SECTORS = ["Technology", "Healthcare", "Finance", "Energy", "Consumer", "Industrial"]
INDUSTRIES = {
    "Technology": ["Software", "Hardware", "Semiconductors", "Internet"],
    "Healthcare": ["Pharmaceuticals", "Biotech", "Medical Devices"],
    "Finance": ["Banking", "Insurance", "Investment"],
    "Energy": ["Oil & Gas", "Renewable Energy", "Utilities"],
    "Consumer": ["Retail", "Food & Beverage", "Automotive"],
    "Industrial": ["Manufacturing", "Aerospace", "Construction"]
}


def format_number_with_suffix(value: float, decimals: int = 2) -> str:
    """
    Format a number with suffix (T, B, M, K).
    
    Args:
        value: Numeric value
        decimals: Number of decimal places
        
    Returns:
        Formatted string like "4.42T", "165.22B", "1.5M"
    """
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


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format a percentage value.
    
    Args:
        value: Percentage value (e.g., 52.41 for 52.41%)
        decimals: Number of decimal places
        
    Returns:
        Formatted string like "52.41%"
    """
    return f"{value:.{decimals}f}%"


def generate_ticker() -> str:
    """Generate a random ticker symbol (3-5 uppercase letters)."""
    length = random.randint(3, 5)
    return ''.join(random.choices(string.ascii_uppercase, k=length))


def generate_fake_company(ticker: str = None) -> Dict[str, Any]:
    """
    Generate a single fake company record in Yahoo Finance format.
    
    Args:
        ticker: Optional ticker symbol. If not provided, generates a random one.
        
    Returns:
        Dictionary with 'key', 'data', and 'metadata' keys.
        The 'data' field contains the Yahoo Finance format structure.
    """
    if not ticker:
        ticker = generate_ticker()
    
    sector = random.choice(SECTORS)
    industry = random.choice(INDUSTRIES[sector])
    
    # Generate base financials (as numbers for calculations)
    market_cap = random.randint(100_000_000, 5_000_000_000_000)  # $100M to $5T
    revenue = int(market_cap * random.uniform(0.1, 2.0))
    net_income = int(revenue * random.uniform(0.05, 0.3))
    gross_profit = int(revenue * random.uniform(0.4, 0.8))
    ebitda = int(revenue * random.uniform(0.2, 0.5))
    total_assets = int(market_cap * random.uniform(0.8, 1.5))
    total_liabilities = int(market_cap * random.uniform(0.3, 0.8))
    equity = total_assets - total_liabilities
    
    # Stock metrics
    price = round(random.uniform(10.0, 500.0), 2)
    shares_outstanding = market_cap / price if price > 0 else 1
    trailing_pe = round(random.uniform(5.0, 50.0), 2)
    forward_pe = round(trailing_pe * random.uniform(0.7, 1.2), 2)
    peg_ratio = round(random.uniform(0.5, 2.0), 2)
    
    # Calculate derived metrics
    price_to_sales = round(market_cap / revenue if revenue > 0 else 0, 2)
    price_to_book = round(market_cap / equity if equity > 0 else 0, 2)
    enterprise_value = int(market_cap * random.uniform(0.95, 1.05))
    enterprise_value_revenue = round(enterprise_value / revenue if revenue > 0 else 0, 2)
    enterprise_value_ebitda = round(enterprise_value / ebitda if ebitda > 0 else 0, 2)
    
    # Financial ratios
    revenue_per_share = round(revenue / shares_outstanding if shares_outstanding > 0 else 0, 2)
    earnings_per_share = round(net_income / shares_outstanding if shares_outstanding > 0 else 0, 2)
    
    # Growth rates (as percentages)
    quarterly_revenue_growth = round(random.uniform(-20.0, 100.0), 2)
    quarterly_earnings_growth = round(random.uniform(-30.0, 150.0), 2)
    
    # Profitability metrics (as percentages)
    profit_margin = round((net_income / revenue * 100) if revenue > 0 else 0, 2)
    operating_margin = round((ebitda / revenue * 100) if revenue > 0 else 0, 2)
    roa = round((net_income / total_assets * 100) if total_assets > 0 else 0, 2)
    roe = round((net_income / equity * 100) if equity > 0 else 0, 2)
    
    # Generate timestamp
    extracted_at = datetime.now().isoformat() + "Z"
    
    # Build Yahoo Finance format structure
    yahoo_data = {
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
            "enterpriseValueEBITDA": f"{enterprise_value_ebitda:.2f}"
        },
        "financials": {
            "revenue": format_number_with_suffix(revenue),
            "revenuePerShare": f"{revenue_per_share:.2f}",
            "quarterlyRevenueGrowth": format_percentage(quarterly_revenue_growth),
            "grossProfit": format_number_with_suffix(gross_profit),
            "ebitda": format_number_with_suffix(ebitda),
            "netIncome": format_number_with_suffix(net_income),
            "earningsPerShare": f"{earnings_per_share:.2f}",
            "quarterlyEarningsGrowth": format_percentage(quarterly_earnings_growth)
        },
        "profitability": {
            "profitMargin": format_percentage(profit_margin),
            "operatingMargin": format_percentage(operating_margin),
            "returnOnAssets": format_percentage(roa),
            "returnOnEquity": format_percentage(roe)
        }
    }
    
    return {
        "key": f"company:{ticker.upper()}",
        "data": yahoo_data,
        "metadata": {
            "source": "seed_data",
            "type": "company",
            "generated_at": extracted_at,
            "sector": sector,
            "industry": industry,
            "ticker": ticker.upper()
        }
    }


def generate_batch(count: int = 100) -> List[Dict[str, Any]]:
    """
    Generate a batch of fake companies with unique tickers.
    
    Args:
        count: Number of companies to generate (default: 100)
        
    Returns:
        List of company dictionaries, each with 'key', 'data', and 'metadata'.
        The 'data' field follows Yahoo Finance format.
    """
    companies = []
    used_tickers = set()
    
    for _ in range(count):
        # Ensure unique tickers
        ticker = generate_ticker()
        while ticker in used_tickers:
            ticker = generate_ticker()
        used_tickers.add(ticker)
        
        companies.append(generate_fake_company(ticker))
    
    return companies
