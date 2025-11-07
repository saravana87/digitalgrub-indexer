"""
Example: Index all data sources
"""
from indexer import index_all_sources
import logging

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    print("Starting incremental indexing for all sources...")
    print("=" * 60)
    
    # Index all sources with incremental updates
    # This will only index records where index_status is NULL or not 'indexed'
    results = index_all_sources(batch_size=100)
    
    print("\n" + "=" * 60)
    print("INDEXING COMPLETE")
    print("=" * 60)
    
    for source, stats in results.items():
        print(f"\n{source.upper()}:")
        if "error" in stats:
            print(f"  ❌ Error: {stats['error']}")
        else:
            print(f"  ✓ Processed: {stats['total_processed']}")
            print(f"  ✓ Indexed: {stats['total_indexed']}")
            print(f"  ✗ Errors: {stats['errors']}")
