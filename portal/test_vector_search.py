"""
Test script for Portal Query Engine with Filters
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.services.query_engine import PortalQueryEngine

def test_filters():
    """Test getting filter options"""
    print("=" * 80)
    print("Testing Portal Query Engine with Filters")
    print("=" * 80)
    
    # Initialize query engine
    print("\n1. Initializing PortalQueryEngine...")
    engine = PortalQueryEngine()
    print("   ✓ Connected to database and Azure OpenAI")
    
    # Get filter options
    print("\n2. Getting available filters...")
    
    print("\n   News Categories:")
    categories = engine.get_news_categories()
    for cat in categories[:10]:  # Show first 10
        print(f"   - {cat}")
    print(f"   ... ({len(categories)} total)")
    
    print("\n   News Sources:")
    sources = engine.get_news_sources()
    for src in sources[:10]:
        print(f"   - {src}")
    print(f"   ... ({len(sources)} total)")
    
    print("\n   Job Sectors:")
    sectors = engine.get_job_sectors()
    for sec in sectors[:10]:
        print(f"   - {sec}")
    print(f"   ... ({len(sectors)} total)")
    
    # Test title generation with filters
    print("\n" + "=" * 80)
    print("3. Testing Title Generation with Filters")
    print("=" * 80)
    
    # Test 1: Jobs without filter
    print("\n[Test 1] Jobs - No Filter")
    print("Topic: 'Software Developer Careers'")
    titles = engine.generate_titles_from_jobs(
        topic="Software Developer Careers",
        sector=None,
        num_titles=3
    )
    for i, title in enumerate(titles, 1):
        print(f"   {i}. {title}")
    
    # Test 2: Jobs with sector filter
    if sectors:
        print(f"\n[Test 2] Jobs - Filtered by Sector: '{sectors[0]}'")
        print("Topic: 'Career Opportunities'")
        titles = engine.generate_titles_from_jobs(
            topic="Career Opportunities",
            sector=sectors[0],
            num_titles=3
        )
        for i, title in enumerate(titles, 1):
            print(f"   {i}. {title}")
    
    # Test 3: News without filter
    print("\n[Test 3] News - No Filter")
    print("Topic: 'Industry Trends'")
    titles = engine.generate_titles_from_news(
        topic="Industry Trends",
        category=None,
        source=None,
        num_titles=3
    )
    for i, title in enumerate(titles, 1):
        print(f"   {i}. {title}")
    
    # Test 4: News with category filter
    if categories:
        print(f"\n[Test 4] News - Filtered by Category: '{categories[0]}'")
        print("Topic: 'Latest News'")
        titles = engine.generate_titles_from_news(
            topic="Latest News",
            category=categories[0],
            source=None,
            num_titles=3
        )
        for i, title in enumerate(titles, 1):
            print(f"   {i}. {title}")
    
    print("\n" + "=" * 80)
    print("✓ All tests completed successfully!")
    print("=" * 80)

if __name__ == "__main__":
    test_filters()
