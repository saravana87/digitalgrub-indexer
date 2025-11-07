"""
Example: Force reindex all data (not incremental)
Use this when you need to rebuild the entire index from scratch
"""
from indexer import JobIndexer, TNNewsIndexer, AIJobIndexer
import logging

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    print("⚠️  WARNING: This will REINDEX ALL records!")
    print("This will reset index_status for all records and rebuild the index.")
    
    response = input("\nAre you sure you want to continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Reindexing cancelled.")
        exit()
    
    print("\nStarting full reindex...")
    print("=" * 60)
    
    indexers = [
        ("Jobs", JobIndexer()),
        ("TN News", TNNewsIndexer()),
        ("AI Jobs", AIJobIndexer()),
    ]
    
    for name, indexer in indexers:
        print(f"\nReindexing {name}...")
        print("-" * 60)
        
        try:
            stats = indexer.reindex_all(batch_size=100)
            print(f"✓ {name} complete:")
            print(f"  - Processed: {stats['total_processed']}")
            print(f"  - Indexed: {stats['total_indexed']}")
            print(f"  - Errors: {stats['errors']}")
        except Exception as e:
            print(f"✗ {name} failed: {str(e)}")
    
    print("\n" + "=" * 60)
    print("REINDEXING COMPLETE")
