"""
Company data generator for seeding test data.

Generates fake company records matching the schema from sample_company_data.json
and sample_stock_data.json.
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


def generate_ticker() -> str:
    """Generate a random ticker symbol (3-5 uppercase letters)."""
    length = random.randint(3, 5)
    return ''.join(random.choices(string.ascii_uppercase, k=length))


def generate_company_name(ticker: str) -> str:
    """Generate a company name based on ticker."""
    suffixes = ["Inc.", "Corp.", "Ltd.", "LLC", "Group", "Holdings"]
    return f"{ticker} {random.choice(suffixes)}"


def generate_fake_company(ticker: str = None) -> Dict[str, Any]:
    """
    Generate a single fake company record.
    
    Args:
        ticker: Optional ticker symbol. If not provided, generates a random one.
        
    Returns:
        Dictionary with 'key', 'data', and 'metadata' keys.
    """
    if not ticker:
        ticker = generate_ticker()
    
    sector = random.choice(SECTORS)
    industry = random.choice(INDUSTRIES[sector])
    
    # Generate realistic financials
    market_cap = random.randint(100_000_000, 5_000_000_000_000)  # $100M to $5T
    revenue = int(market_cap * random.uniform(0.1, 2.0))
    net_income = int(revenue * random.uniform(0.05, 0.3))
    employees = random.randint(50, 500_000)
    
    # Stock metrics
    price = round(random.uniform(10.0, 500.0), 2)
    pe_ratio = round(random.uniform(5.0, 50.0), 2)
    dividend_yield = round(random.uniform(0.0, 5.0), 2)
    
    return {
        "key": f"company:{ticker}",
        "data": {
            "company": {
                "name": generate_company_name(ticker),
                "symbol": ticker,
                "sector": sector,
                "industry": industry,
                "employees": employees
            },
            "financials": {
                "revenue": revenue,
                "net_income": net_income,
                "total_assets": int(market_cap * random.uniform(0.8, 1.5)),
                "total_liabilities": int(market_cap * random.uniform(0.3, 0.8))
            },
            "stock_metrics": {
                "ticker": ticker,
                "price": price,
                "volume": random.randint(100_000, 10_000_000),
                "market_cap": market_cap,
                "pe_ratio": pe_ratio,
                "dividend_yield": dividend_yield,
                "timestamp": datetime.now().isoformat()
            }
        },
        "metadata": {
            "source": "seed_data",
            "type": "company",
            "generated_at": datetime.now().isoformat(),
            "sector": sector,
            "industry": industry
        }
    }


def generate_batch(count: int = 100) -> List[Dict[str, Any]]:
    """
    Generate a batch of fake companies with unique tickers.
    
    Args:
        count: Number of companies to generate (default: 100)
        
    Returns:
        List of company dictionaries, each with 'key', 'data', and 'metadata'.
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

