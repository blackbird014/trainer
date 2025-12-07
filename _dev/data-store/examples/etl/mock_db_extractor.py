"""
Mock external database extractor for ETL.

Simulates extracting data from an external database.
Easy to replace with real database connector later.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
import random


class MockDBExtractor:
    """Mock external database extractor."""
    
    def __init__(self, db_name: str = "mock_external_db"):
        """
        Initialize mock DB extractor.
        
        Args:
            db_name: Name of the mock database
        """
        self.db_name = db_name
        self._sample_data = self._generate_sample_data()
    
    def _generate_sample_data(self) -> List[Dict]:
        """Generate sample data to simulate database records."""
        tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
        
        data = []
        for ticker in tickers:
            data.append({
                "ticker": ticker,
                "price": round(random.uniform(100, 500), 2),
                "volume": random.randint(1000000, 10000000),
                "market_cap": random.randint(100000000000, 3000000000000),
                "pe_ratio": round(random.uniform(15, 35), 2),
                "dividend_yield": round(random.uniform(0.1, 3.0), 2),
                "timestamp": datetime.now().isoformat()
            })
        
        return data
    
    def extract_all(self) -> List[Dict]:
        """
        Extract all records from mock database.
        
        Returns:
            List of records as dictionaries
        """
        return self._sample_data.copy()
    
    def extract_by_ticker(self, ticker: str) -> Optional[Dict]:
        """
        Extract record by ticker symbol.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Record dictionary or None if not found
        """
        for record in self._sample_data:
            if record["ticker"] == ticker:
                return record.copy()
        return None
    
    def extract_by_filter(self, filters: Dict) -> List[Dict]:
        """
        Extract records matching filters.
        
        Args:
            filters: Dictionary of filter criteria
            
        Returns:
            List of matching records
        """
        results = []
        for record in self._sample_data:
            match = True
            for key, value in filters.items():
                if key not in record or record[key] != value:
                    match = False
                    break
            if match:
                results.append(record.copy())
        return results
    
    def get_metadata(self) -> Dict:
        """Get metadata about the mock database."""
        return {
            "source": "mock_external_db",
            "db_name": self.db_name,
            "record_count": len(self._sample_data),
            "extracted_at": datetime.now().isoformat(),
            "available_tickers": [r["ticker"] for r in self._sample_data]
        }


def example_usage():
    """Example usage of mock DB extractor."""
    extractor = MockDBExtractor()
    
    print("=== Mock DB Extractor Example ===\n")
    
    # Extract all records
    print("1. Extracting all records...")
    all_records = extractor.extract_all()
    print(f"   Found {len(all_records)} records")
    for record in all_records[:3]:  # Show first 3
        print(f"   - {record['ticker']}: ${record['price']}")
    
    # Extract by ticker
    print("\n2. Extracting by ticker...")
    aapl = extractor.extract_by_ticker("AAPL")
    if aapl:
        print(f"   AAPL: ${aapl['price']}, Volume: {aapl['volume']:,}")
    
    # Extract by filter
    print("\n3. Extracting by filter (price > 200)...")
    expensive = [r for r in all_records if r["price"] > 200]
    print(f"   Found {len(expensive)} expensive stocks")
    for record in expensive:
        print(f"   - {record['ticker']}: ${record['price']}")
    
    # Get metadata
    print("\n4. Database metadata...")
    metadata = extractor.get_metadata()
    print(f"   Source: {metadata['source']}")
    print(f"   Records: {metadata['record_count']}")
    print(f"   Tickers: {metadata['available_tickers']}")


if __name__ == "__main__":
    example_usage()

