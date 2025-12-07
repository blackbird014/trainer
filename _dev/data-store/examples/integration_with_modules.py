"""
Integration example showing data-store with other modules.

Demonstrates:
- data-retriever → data-store (automatic storage)
- prompt-manager → data-store (querying stored data)
- format-converter → data-store (storing formatted outputs)
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from data_store import create_store
    from data_retriever import FileRetriever, DataCache
    from format_converter import FormatConverter
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Make sure modules are installed:")
    print("  pip install -e ../data-retriever")
    print("  pip install -e ../data-store")
    print("  pip install -e ../format-converter")
    sys.exit(1)


def integration_example():
    """Integration example with data-store."""
    print("=" * 80)
    print("Data-Store Integration Example")
    print("=" * 80)
    print()

    # 1. Initialize Data Store
    print("Step 1: Initializing Data Store...")
    try:
        # Try MongoDB first
        store = create_store(
            "mongodb",
            connection_string="mongodb://localhost:27017",
            database="trainer_data"
        )
        print("✓ MongoDB store initialized")
    except Exception:
        # Fallback to SQLite
        store = create_store("sqlite", database_path="data/integration.db")
        print("✓ SQLite store initialized")

    # 2. Initialize Data Retriever
    print("\nStep 2: Initializing Data Retriever...")
    cache = DataCache(default_ttl=3600)
    retriever = FileRetriever(
        base_path="../../output/json",
        cache=cache
    )
    print("✓ Data retriever initialized")

    # 3. Retrieve and Store Data
    print("\nStep 3: Retrieving data and storing in data-store...")
    result = retriever.retrieve_with_cache({
        "path": "stock_data_20251121_122508.json"
    })

    if result.success:
        # Store in data-store
        key = "stock_data:20251121:122508"
        store.store(
            key=key,
            data=result.data,
            metadata={
                "source": "file_retriever",
                "file_path": "stock_data_20251121_122508.json",
                "data_type": "stock_data"
            }
        )
        print(f"✓ Data stored with key: {key}")

        # Verify storage
        stored = store.retrieve(key)
        if stored:
            print(f"✓ Verified: Retrieved from store")
            print(f"  Source: {stored.source}")
            print(f"  Stored at: {stored.stored_at}")
    else:
        print(f"⚠ Could not retrieve data: {result.error}")
        print("  Using sample data for demonstration...")
        # Use sample data
        sample_data = {
            "content": [
                {"ticker": "AAPL", "price": 150.25},
                {"ticker": "MSFT", "price": 380.50}
            ]
        }
        key = "sample:stock_data"
        store.store(
            key=key,
            data=sample_data,
            metadata={"source": "sample", "data_type": "stock_data"}
        )
        print(f"✓ Sample data stored")

    # 4. Query Data Store (as prompt-manager would)
    print("\nStep 4: Querying data-store (simulating prompt-manager)...")
    query_result = store.query({"source": "file_retriever"})
    if query_result.total == 0:
        query_result = store.query({"source": "sample"})
    
    print(f"✓ Found {query_result.total} items")
    for item in query_result.items[:3]:
        print(f"  - {item.key}: {item.source}")

    # 5. Use Data in Format Converter
    print("\nStep 5: Using data-store data with format-converter...")
    converter = FormatConverter()
    
    # Get data from store
    stored_data = store.retrieve(key)
    if stored_data:
        # Convert data to markdown
        markdown = converter.convert(
            stored_data.data,
            source_format="json",
            target_format="markdown"
        )
        print(f"✓ Converted to markdown ({len(markdown)} chars)")

        # Convert to HTML
        html = converter.convert(
            markdown,
            source_format="markdown",
            target_format="html"
        )
        print(f"✓ Converted to HTML ({len(html)} bytes)")

        # Store formatted output
        output_key = f"{key}:formatted"
        store.store(
            key=output_key,
            data={"html": html, "markdown": markdown},
            metadata={
                "source": "format_converter",
                "original_key": key,
                "formats": ["markdown", "html"]
            }
        )
        print(f"✓ Formatted output stored: {output_key}")

    # 6. Analytics Example
    print("\nStep 6: Analytics on stored data...")
    total_items = store.count({})
    file_items = store.count({"source": "file_retriever"})
    sample_items = store.count({"source": "sample"})
    
    print(f"✓ Total items in store: {total_items}")
    print(f"  - From file_retriever: {file_items}")
    print(f"  - From sample: {sample_items}")

    # 7. Summary
    print("\n" + "=" * 80)
    print("Integration Complete!")
    print("=" * 80)
    print()
    print("Data Flow:")
    print("  1. data-retriever → retrieves data")
    print("  2. data-store → persists data")
    print("  3. prompt-manager → queries data-store (not shown, but would query)")
    print("  4. format-converter → uses data from store")
    print("  5. data-store → stores formatted outputs")
    print()
    print("Benefits:")
    print("  ✓ Data persists across restarts")
    print("  ✓ Decouples retrieval from consumption")
    print("  ✓ Multiple modules can access same data")
    print("  ✓ Enables analytics and ETL pipelines")


if __name__ == "__main__":
    try:
        integration_example()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

