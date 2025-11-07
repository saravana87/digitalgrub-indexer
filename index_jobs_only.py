"""
Example: Index only Jobs table
"""
from indexer import JobIndexer
import logging

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    print("Starting incremental indexing for Jobs...")
    print("=" * 60)
    
    # Create jobs indexer
    indexer = JobIndexer()
    
    # Index jobs with incremental updates
    # This will only index records where index_status is NULL or not '0'
    stats = indexer.index_records(batch_size=100)
    
    print("\n" + "=" * 60)
    print("INDEXING COMPLETE - JOBS")
    print("=" * 60)
    print(f"✓ Processed: {stats['total_processed']}")
    print(f"✓ Indexed: {stats['total_indexed']}")
    print(f"✗ Errors: {stats['errors']}")
