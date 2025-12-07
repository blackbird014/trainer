"""
Visualize ETL Pipeline Results

Shows what data has been stored by the ETL pipeline.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from data_store import create_store
from datetime import datetime


def visualize_pipeline_results():
    """Visualize what's stored in the data store from ETL pipeline."""
    print("=" * 80)
    print("🔍 ETL Pipeline Visualization")
    print("=" * 80)
    print()
    
    # Initialize store (same as pipeline)
    try:
        store = create_store(
            "mongodb",
            connection_string="mongodb://localhost:27017",
            database="trainer_data",
            collection="etl_data"
        )
        backend = "MongoDB"
    except Exception:
        store = create_store("sqlite", database_path="data/etl_pipeline.db")
        backend = "SQLite"
    
    print(f"📦 Connected to: {backend}")
    print()
    
    # Get all items
    all_items = store.query({}, limit=100)
    
    if all_items.total == 0:
        print("❌ No data found in store")
        print("\n💡 Run the pipeline first:")
        print("   python simple_pipeline.py")
        return
    
    print(f"✅ Found {all_items.total} items in store\n")
    
    # Group by source
    sources = {}
    for item in all_items.items:
        source = item.source
        if source not in sources:
            sources[source] = []
        sources[source].append(item)
    
    # Display by source with details
    for source, items in sources.items():
        print("=" * 80)
        print(f"📦 Source: {source.upper()}")
        print("=" * 80)
        print(f"   Items: {len(items)}\n")
        
        for i, item in enumerate(items, 1):
            print(f"   [{i}] Key: {item.key}")
            print(f"       Stored: {item.stored_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"       Updated: {item.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"       Version: {item.version}")
            
            # Show data preview based on type
            if isinstance(item.data, dict):
                if "ticker" in item.data:
                    # Stock data
                    print(f"       📈 Ticker: {item.data.get('ticker', 'N/A')}")
                    print(f"       💰 Price: ${item.data.get('price', 'N/A')}")
                    print(f"       📊 Volume: {item.data.get('volume', 'N/A'):,}" if item.data.get('volume') else "")
                elif "content" in item.data:
                    # File data with content array
                    content = item.data.get('content', [])
                    print(f"       📄 Content items: {len(content)}")
                    if content:
                        first_item = content[0] if isinstance(content, list) else content
                        if isinstance(first_item, dict):
                            print(f"       📋 First item keys: {', '.join(list(first_item.keys())[:5])}")
                else:
                    # Generic dict
                    keys = list(item.data.keys())[:5]
                    print(f"       🔑 Data keys: {', '.join(keys)}")
                    if len(item.data.keys()) > 5:
                        print(f"          ... and {len(item.data.keys()) - 5} more")
            
            # Show metadata
            if item.metadata:
                meta_keys = list(item.metadata.keys())[:5]
                print(f"       🏷️  Metadata: {', '.join(meta_keys)}")
            
            print()
    
    # Summary statistics
    print("=" * 80)
    print("📊 Summary Statistics")
    print("=" * 80)
    print(f"   Total items: {all_items.total}")
    print(f"   Unique sources: {len(sources)}")
    for source, items in sources.items():
        print(f"   - {source}: {len(items)} items")
    
    # Data freshness
    print("\n⏰ Data Freshness:")
    for source, items in sources.items():
        if items:
            latest = max(items, key=lambda x: x.updated_at)
            oldest = min(items, key=lambda x: x.updated_at)
            print(f"   {source}:")
            print(f"      Latest: {latest.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"      Oldest: {oldest.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n✅ Visualization complete!")


if __name__ == "__main__":
    try:
        visualize_pipeline_results()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

