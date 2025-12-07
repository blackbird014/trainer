"""
Basic usage examples for data-store module.

Note: All examples use SQLite by default (no external dependencies required).
The MongoDB example is optional and will gracefully skip if MongoDB is not available.

To run all examples:
    python basic_usage.py

The MongoDB example will automatically skip if:
    - pymongo is not installed (pip install trainer-data-store[mongodb])
    - MongoDB is not running locally
"""

from data_store import create_store
from data_store.models import StoredData


def example_sqlite_store():
    """Example: Using SQLite store."""
    print("=== SQLite Store Example ===")
    
    # Create SQLite store (perfect for development)
    store = create_store("sqlite", database_path="data/example.db")
    
    # Store data
    key = store.store(
        key="user:123",
        data={"name": "John Doe", "email": "john@example.com"},
        metadata={"source": "api", "created_by": "system"}
    )
    print(f"Stored data with key: {key}")
    
    # Retrieve data
    stored = store.retrieve("user:123")
    if stored:
        print(f"Retrieved: {stored.data}")
        print(f"Source: {stored.source}")
        print(f"Stored at: {stored.stored_at}")
    
    # Update data
    store.update("user:123", {"name": "John Doe", "email": "john.doe@example.com"})
    updated = store.retrieve("user:123")
    print(f"Updated: {updated.data}")
    print(f"Version: {updated.version}")
    
    # Query data
    result = store.query({"source": "api"})
    print(f"Found {result.total} items with source='api'")
    
    # Delete data
    store.delete("user:123")
    print("Data deleted")


def example_mongodb_store():
    """Example: Using MongoDB store."""
    print("\n=== MongoDB Store Example ===")
    print("Note: This example requires MongoDB to be running.")
    print("To run MongoDB locally:")
    print("  1. Install MongoDB: https://www.mongodb.com/try/download/community")
    print("  2. Or use Docker: docker run -d -p 27017:27017 --name mongodb mongo")
    print("  3. Install Python package: pip install trainer-data-store[mongodb]")
    print()
    
    try:
        # Check if pymongo is available
        import pymongo
    except ImportError:
        print("❌ MongoDB support not available.")
        print("   Install with: pip install trainer-data-store[mongodb]")
        print("   Skipping MongoDB example...")
        return
    
    try:
        # Create MongoDB store (requires pymongo and running MongoDB)
        print("Attempting to connect to MongoDB at mongodb://localhost:27017...")
        store = create_store(
            "mongodb",
            connection_string="mongodb://localhost:27017",
            database="example_db"
        )
        
        # Test connection
        store.store("__test__", {"test": True}, ttl=1)
        store.delete("__test__")
        print("✅ Connected to MongoDB successfully!")
        
        # Store data
        key = store.store(
            key="stock:AAPL",
            data={"price": 150.25, "volume": 1000000},
            metadata={"source": "yahoo_finance", "ticker": "AAPL"}
        )
        print(f"Stored stock data with key: {key}")
        
        # Query by source
        result = store.query({"source": "yahoo_finance"})
        print(f"Found {result.total} items from yahoo_finance")
        
        # Use aggregation (MongoDB-specific)
        pipeline = [
            {"$match": {"source": "yahoo_finance"}},
            {"$group": {"_id": "$source", "count": {"$sum": 1}}}
        ]
        aggregated = store.aggregate(pipeline)
        print(f"Aggregation result: {aggregated}")
        
        # Cleanup
        store.delete("stock:AAPL")
        print("Cleaned up test data")
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("   Make sure MongoDB is running:")
        print("   - Check if MongoDB service is running")
        print("   - Or start Docker container: docker start mongodb")
        print("   - Or start MongoDB manually")
        print("   Skipping MongoDB example...")


def example_bulk_operations():
    """Example: Bulk operations."""
    print("\n=== Bulk Operations Example ===")
    
    store = create_store("sqlite", database_path="data/bulk_example.db")
    
    # Bulk store
    items = [
        {"key": "item:1", "data": {"value": 1}, "metadata": {"source": "batch"}},
        {"key": "item:2", "data": {"value": 2}, "metadata": {"source": "batch"}},
        {"key": "item:3", "data": {"value": 3}, "metadata": {"source": "batch"}},
    ]
    
    result = store.bulk_store(items)
    print(f"Bulk stored {result.records_loaded} items")
    print(f"Keys: {result.keys}")
    
    # Count items
    count = store.count({"source": "batch"})
    print(f"Total items with source='batch': {count}")
    
    # Get distinct values
    distinct = store.distinct("value", {"source": "batch"})
    print(f"Distinct values: {distinct}")


def example_ttl():
    """Example: Using TTL (time-to-live)."""
    print("\n=== TTL Example ===")
    
    store = create_store("sqlite", database_path="data/ttl_example.db")
    
    # Store with TTL (expires in 5 seconds)
    key = store.store(
        key="temp:data",
        data={"temp": True},
        ttl=5
    )
    print(f"Stored temporary data with key: {key}")
    
    # Check if exists
    print(f"Exists: {store.exists(key)}")
    
    # Retrieve (should work immediately)
    stored = store.retrieve(key)
    if stored:
        print(f"Retrieved before expiry: {stored.data}")
    
    print("Note: Data will expire after 5 seconds")


def example_freshness():
    """Example: Checking data freshness."""
    print("\n=== Freshness Example ===")
    
    store = create_store("sqlite", database_path="data/freshness_example.db")
    
    # Store data
    key = store.store("data:1", {"value": 1})
    
    # Get freshness
    freshness = store.get_freshness(key)
    print(f"Data freshness: {freshness}")
    
    # Update data
    import time
    time.sleep(0.1)
    store.update(key, {"value": 2})
    
    # Check freshness again
    new_freshness = store.get_freshness(key)
    print(f"Updated freshness: {new_freshness}")
    print(f"Freshness changed: {new_freshness > freshness}")


if __name__ == "__main__":
    import sys
    
    # Check if user wants MongoDB examples
    use_mongodb = "--mongodb" in sys.argv or "-m" in sys.argv
    
    # Run SQLite example (always works)
    example_sqlite_store()
    
    # Run MongoDB example if requested
    if use_mongodb:
        example_mongodb_store()
    else:
        print("\n=== MongoDB Store Example ===")
        print("Skipped (use --mongodb or -m flag to run)")
        print("To run MongoDB examples:")
        print("  1. Setup MongoDB: ./setup_mongodb.sh")
        print("  2. Install package: pip install trainer-data-store[mongodb]")
        print("  3. Run: python basic_usage.py --mongodb")
        print("  4. Or see: python examples/mongodb_json_storage.py")
        print()
    
    # Run other examples (all use SQLite, no external dependencies)
    example_bulk_operations()
    example_ttl()
    example_freshness()
    
    print("\n✅ All examples completed!")
    if not use_mongodb:
        print("\n💡 Tip: For JSON data storage, MongoDB is recommended.")
        print("   See: python examples/mongodb_json_storage.py")

