"""
MongoDB JSON Storage Example

Demonstrates storing and querying JSON data in MongoDB.
Perfect for storing data retrieved from APIs, scrapers, etc.
"""

from data_store import create_store
from datetime import datetime
import json


def example_store_json_data():
    """Example: Store JSON data from various sources."""
    print("=== MongoDB JSON Storage Example ===\n")
    
    # Create MongoDB store
    print("Connecting to MongoDB...")
    store = create_store(
        "mongodb",
        connection_string="mongodb://localhost:27017",
        database="trainer_data",
        collection="json_data"
    )
    print("✅ Connected to MongoDB\n")
    
    # Example 1: Store stock data (from Yahoo Finance)
    print("1. Storing stock data (JSON format)...")
    stock_data = {
        "ticker": "AAPL",
        "price": 150.25,
        "volume": 1000000,
        "market_cap": 2500000000000,
        "pe_ratio": 28.5,
        "dividend_yield": 0.5,
        "timestamp": datetime.now().isoformat()
    }
    
    key1 = store.store(
        key="stock:AAPL:20240101",
        data=stock_data,
        metadata={
            "source": "yahoo_finance",
            "ticker": "AAPL",
            "date": "2024-01-01",
            "data_type": "stock_quote"
        }
    )
    print(f"   ✅ Stored: {key1}")
    
    # Example 2: Store multiple stocks
    stocks = [
        {"ticker": "MSFT", "price": 380.50, "volume": 2000000},
        {"ticker": "GOOGL", "price": 140.75, "volume": 1500000},
        {"ticker": "AMZN", "price": 145.20, "volume": 3000000},
    ]
    
    print("\n2. Storing multiple stocks...")
    for stock in stocks:
        key = store.store(
            key=f"stock:{stock['ticker']}:20240101",
            data=stock,
            metadata={
                "source": "yahoo_finance",
                "ticker": stock["ticker"],
                "date": "2024-01-01",
                "data_type": "stock_quote"
            }
        )
        print(f"   ✅ Stored: {key}")
    
    # Example 3: Store API response (nested JSON)
    print("\n3. Storing nested JSON from API...")
    api_response = {
        "status": "success",
        "data": {
            "company": {
                "name": "Apple Inc.",
                "symbol": "AAPL",
                "sector": "Technology",
                "employees": 164000
            },
            "financials": {
                "revenue": 394328000000,
                "net_income": 99803000000,
                "assets": 352755000000
            }
        },
        "metadata": {
            "api_version": "v1",
            "request_id": "req_12345",
            "timestamp": datetime.now().isoformat()
        }
    }
    
    key2 = store.store(
        key="api:company:AAPL:20240101",
        data=api_response,
        metadata={
            "source": "company_api",
            "ticker": "AAPL",
            "date": "2024-01-01",
            "data_type": "company_info"
        }
    )
    print(f"   ✅ Stored: {key2}")
    
    # Example 4: Query by source
    print("\n4. Querying data by source...")
    result = store.query({"source": "yahoo_finance"})
    print(f"   Found {result.total} items from yahoo_finance")
    for item in result.items[:3]:  # Show first 3
        print(f"   - {item.key}: {item.data.get('ticker', 'N/A')} @ ${item.data.get('price', 'N/A')}")
    
    # Example 5: Query by data type
    print("\n5. Querying by data type...")
    result = store.query({"data_type": "stock_quote"})
    print(f"   Found {result.total} stock quotes")
    
    # Example 6: Query nested JSON fields (MongoDB-specific)
    print("\n6. Querying nested JSON fields...")
    # MongoDB allows querying nested fields
    result = store.query({"ticker": "AAPL"})  # This searches in metadata
    print(f"   Found {result.total} items for AAPL")
    
    # Example 7: Aggregation pipeline (MongoDB-specific)
    print("\n7. Using MongoDB aggregation...")
    pipeline = [
        {"$match": {"source": "yahoo_finance"}},
        {"$group": {
            "_id": "$source",
            "total_items": {"$sum": 1},
            "avg_price": {"$avg": "$data.price"}
        }}
    ]
    aggregated = store.aggregate(pipeline)
    print(f"   Aggregation result:")
    for result in aggregated:
        print(f"   - Source: {result.get('_id')}")
        print(f"     Total items: {result.get('total_items')}")
        print(f"     Avg price: ${result.get('avg_price', 0):.2f}")
    
    # Example 8: Get distinct values
    print("\n8. Getting distinct tickers...")
    distinct_tickers = store.distinct("ticker", {"source": "yahoo_finance"})
    print(f"   Distinct tickers: {distinct_tickers}")
    
    # Example 9: Count items
    print("\n9. Counting items...")
    total_count = store.count({})
    yahoo_count = store.count({"source": "yahoo_finance"})
    print(f"   Total items: {total_count}")
    print(f"   Yahoo Finance items: {yahoo_count}")
    
    # Example 10: Retrieve specific item
    print("\n10. Retrieving specific item...")
    stored = store.retrieve("stock:AAPL:20240101")
    if stored:
        print(f"   Key: {stored.key}")
        print(f"   Data: {json.dumps(stored.data, indent=2)}")
        print(f"   Source: {stored.source}")
        print(f"   Stored at: {stored.stored_at}")
        print(f"   Version: {stored.version}")
    
    # Example 11: Update data
    print("\n11. Updating data...")
    updated_data = stock_data.copy()
    updated_data["price"] = 151.00  # Updated price
    updated_data["timestamp"] = datetime.now().isoformat()
    
    store.update("stock:AAPL:20240101", updated_data)
    updated = store.retrieve("stock:AAPL:20240101")
    print(f"   Updated price: ${updated.data['price']}")
    print(f"   Version incremented: {updated.version}")
    
    print("\n✅ All examples completed!")
    print("\nNote: Data is stored in MongoDB and persists across restarts.")
    print("To view data in MongoDB:")
    print("  docker exec -it mongodb mongosh trainer_data")
    print("  db.json_data.find().pretty()")


if __name__ == "__main__":
    try:
        example_store_json_data()
    except ImportError as e:
        print("❌ Error: MongoDB support not available")
        print("   Install with: pip install trainer-data-store[mongodb]")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure MongoDB is running:")
        print("  Run: ./setup_mongodb.sh")
        print("  Or: docker start mongodb")

