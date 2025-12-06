#!/usr/bin/env python3
"""
Basic usage examples for data-retriever module.
"""

from data_retriever import FileRetriever, APIRetriever, DataCache


def example_file_retriever():
    """Example: Reading a file."""
    print("=" * 60)
    print("File Retriever Example")
    print("=" * 60)

    retriever = FileRetriever(base_path="../../output/json")

    # Read a JSON file
    result = retriever.retrieve({"path": "stock_data_20251121_122508.json"})

    if result.success:
        print(f"✓ Successfully read file")
        print(f"  Format: {result.data['format']}")
        print(f"  Content type: {type(result.data['content'])}")
        if isinstance(result.data['content'], list):
            print(f"  Number of items: {len(result.data['content'])}")
    else:
        print(f"✗ Error: {result.error}")


def example_api_retriever():
    """Example: Making an API request."""
    print("\n" + "=" * 60)
    print("API Retriever Example")
    print("=" * 60)

    retriever = APIRetriever()

    # Example: GET request to a public API
    result = retriever.retrieve({
        "url": "https://api.github.com/repos/octocat/Hello-World",
    })

    if result.success:
        print(f"✓ Successfully retrieved data")
        print(f"  Status code: {result.data['status_code']}")
        print(f"  Repository: {result.data['data'].get('full_name', 'N/A')}")
    else:
        print(f"✗ Error: {result.error}")


def example_with_cache():
    """Example: Using cache."""
    print("\n" + "=" * 60)
    print("Caching Example")
    print("=" * 60)

    cache = DataCache(default_ttl=60)  # 1 minute cache
    retriever = FileRetriever(
        base_path="../../output/json",
        cache=cache
    )

    query = {"path": "stock_data_20251121_122508.json"}

    # First call - reads from file
    print("First call (from file):")
    result1 = retriever.retrieve_with_cache(query)
    print(f"  Success: {result1.success}")

    # Second call - uses cache
    print("\nSecond call (from cache):")
    result2 = retriever.retrieve_with_cache(query)
    print(f"  Success: {result2.success}")
    print(f"  Cache size: {cache.size()}")


if __name__ == "__main__":
    try:
        example_file_retriever()
        example_api_retriever()
        example_with_cache()
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()

