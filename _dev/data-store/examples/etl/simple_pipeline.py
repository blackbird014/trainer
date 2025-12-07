"""
Simple ETL Pipeline Example

Demonstrates:
1. Polling file system for JSON files
2. Extracting from mock external database
3. Storing everything in MongoDB via data-store
"""

from typing import Dict
from data_store import create_store
from file_poller import FilePoller
from mock_db_extractor import MockDBExtractor
import time


def create_pipeline():
    """Create and configure the ETL pipeline."""
    
    # 1. Initialize data store (MongoDB or SQLite)
    print("🔧 Setting up data store...")
    try:
        # Try MongoDB first
        store = create_store(
            "mongodb",
            connection_string="mongodb://localhost:27017",
            database="trainer_data",
            collection="etl_data"
        )
        print("✅ Connected to MongoDB\n")
    except Exception as e:
        # Fallback to SQLite
        print(f"⚠ MongoDB not available ({e})")
        print("   Using SQLite for local development...")
        store = create_store("sqlite", database_path="data/etl_pipeline.db")
        print("✅ SQLite store initialized\n")
    
    # 2. Initialize file poller
    print("🔧 Setting up file poller...")
    poller = FilePoller("data/input", poll_interval=5)
    print("✅ File poller ready\n")
    
    # 3. Initialize mock DB extractor
    print("🔧 Setting up mock DB extractor...")
    db_extractor = MockDBExtractor("mock_stock_db")
    print("✅ Mock DB extractor ready\n")
    
    return store, poller, db_extractor


def process_file_data(data: Dict, metadata: Dict, store):
    """
    Process data from file system.
    
    Args:
        data: JSON data from file
        metadata: File metadata
        store: Data store instance
    """
    # Generate key from filename
    key = f"file:{metadata['file_name']}"
    
    # Store in data store
    store.store(
        key=key,
        data=data,
        metadata={
            **metadata,
            "source": "file_system",
            "pipeline": "simple_etl"
        }
    )
    print(f"   💾 Stored: {key}")
    print(f"      Data keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
    print(f"      File size: {metadata.get('file_size', 0)} bytes")


def process_db_data(store, db_extractor):
    """
    Process data from mock database.
    
    Args:
        store: Data store instance
        db_extractor: Mock DB extractor instance
    """
    print("📊 Extracting from mock database...")
    
    # Extract all records
    records = db_extractor.extract_all()
    db_metadata = db_extractor.get_metadata()
    
    print(f"   Found {len(records)} records")
    
    # Store each record
    for record in records:
        key = f"db:{db_metadata['source']}:{record['ticker']}"
        
        store.store(
            key=key,
            data=record,
            metadata={
                **db_metadata,
                "ticker": record["ticker"],
                "pipeline": "simple_etl"
            }
        )
        print(f"   💾 Stored: {key} - {record['ticker']} @ ${record['price']}")
    
    print(f"✅ Stored {len(records)} records from mock DB\n")


def visualize_store_contents(store):
    """Visualize what's stored in the data store."""
    print("\n" + "=" * 60)
    print("📊 Data Store Contents Visualization")
    print("=" * 60)
    
    # Get all items
    all_items = store.query({}, limit=50)
    print(f"\nTotal items in store: {all_items.total}\n")
    
    if all_items.total == 0:
        print("   (Store is empty)")
        return
    
    # Group by source
    sources = {}
    for item in all_items.items:
        source = item.source
        if source not in sources:
            sources[source] = []
        sources[source].append(item)
    
    # Display by source
    for source, items in sources.items():
        print(f"📦 Source: {source} ({len(items)} items)")
        for item in items[:5]:  # Show first 5
            print(f"   ├─ Key: {item.key}")
            print(f"   │  Stored: {item.stored_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   │  Version: {item.version}")
            
            # Show data preview
            if isinstance(item.data, dict):
                data_keys = list(item.data.keys())[:3]
                print(f"   │  Data keys: {', '.join(data_keys)}")
                if "ticker" in item.data:
                    print(f"   │  Ticker: {item.data.get('ticker', 'N/A')}")
                if "price" in item.data:
                    print(f"   │  Price: ${item.data.get('price', 'N/A')}")
            print(f"   └─ Metadata: {list(item.metadata.keys())[:3]}")
        if len(items) > 5:
            print(f"   └─ ... and {len(items) - 5} more items")
        print()
    
    # Summary statistics
    print("📈 Statistics:")
    print(f"   Total items: {all_items.total}")
    for source in sources.keys():
        count = store.count({"source": source})
        print(f"   - {source}: {count} items")
    print()


def run_pipeline_once(store, poller, db_extractor):
    """Run the ETL pipeline once."""
    print("=" * 60)
    print("🚀 Running ETL Pipeline")
    print("=" * 60 + "\n")
    
    # Step 1: Process files
    print("📁 Step 1: Processing files from filesystem...")
    files_processed = 0
    def file_callback(data, metadata):
        nonlocal files_processed
        process_file_data(data, metadata, store)
        files_processed += 1
    
    poller.poll_once(file_callback)
    if files_processed == 0:
        print("   ℹ️  No new or modified files found")
        print("   💡 Tip: Add JSON files to 'data/input/' directory")
    
    # Step 2: Process mock DB
    print("\n💾 Step 2: Processing mock database...")
    process_db_data(store, db_extractor)
    
    # Step 3: Visualize stored data
    print("\n📊 Step 3: Visualizing stored data...")
    visualize_store_contents(store)
    
    print("✅ Pipeline completed!\n")


def run_pipeline_continuous(store, poller, db_extractor):
    """Run the ETL pipeline continuously."""
    print("=" * 60)
    print("🔄 Running Continuous ETL Pipeline")
    print("=" * 60 + "\n")
    
    # Process mock DB once
    process_db_data(store, db_extractor)
    
    # Then continuously poll files
    print("👀 Starting continuous file polling...")
    print("   (Mock DB data already loaded)")
    print("   (Add JSON files to 'data/input/' directory to process them)\n")
    
    def file_callback(data, metadata):
        process_file_data(data, metadata, store)
    
    try:
        poller.poll_continuously(file_callback)
    except KeyboardInterrupt:
        print("\n🛑 Pipeline stopped")


def main():
    """Main entry point."""
    import sys
    
    # Create pipeline components
    result = create_pipeline()
    if result is None:
        return
    
    store, poller, db_extractor = result
    
    # Run mode
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        run_pipeline_continuous(store, poller, db_extractor)
    else:
        run_pipeline_once(store, poller, db_extractor)
        
        print("💡 Tip: Run with --continuous to watch for new files:")
        print("   python simple_pipeline.py --continuous")


if __name__ == "__main__":
    main()

