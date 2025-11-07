"""
Example: Generate blog content
"""
from query_engine import ContentGenerator
import json

def main():
    # Initialize content generator
    generator = ContentGenerator()
    
    print("DigitalGrub Content Generator")
    print("=" * 60)
    
    # Example 1: Generate blog titles
    print("\n1. GENERATING BLOG TITLES")
    print("-" * 60)
    
    titles = generator.generate_blog_title(
        topic="Data Science Jobs",
        source="jobs",
        num_suggestions=5
    )
    
    print("Suggested Titles:")
    for i, title in enumerate(titles, 1):
        print(f"  {i}. {title}")
    
    # Example 2: Generate blog content
    print("\n2. GENERATING BLOG CONTENT")
    print("-" * 60)
    
    blog = generator.generate_blog_content(
        title="Top 10 High-Paying Tech Jobs in 2025",
        source="jobs",
        word_count=800,
        style="listicle"
    )
    
    print(f"Title: {blog['title']}")
    print(f"Word Count: {blog['word_count']}")
    print(f"\nSummary:\n{blog['summary']}")
    print(f"\nTags: {', '.join(blog['tags'])}")
    print(f"\nContent Preview:\n{blog['content'][:300]}...")
    
    # Example 3: Trend Analysis
    print("\n3. TREND ANALYSIS")
    print("-" * 60)
    
    trends = generator.generate_trend_analysis(
        topic="Remote Work",
        source="jobs"
    )
    
    print(f"Trends Preview:\n{trends[:400]}...")
    
    # Example 4: Search Similar Content
    print("\n4. SEARCH SIMILAR CONTENT")
    print("-" * 60)
    
    similar = generator.search_similar_content(
        query="Machine Learning Engineer with Python",
        source="jobs",
        top_k=3
    )
    
    print(f"Found {len(similar)} similar results:")
    for i, result in enumerate(similar, 1):
        print(f"\n  Result {i} (Score: {result['score']:.3f}):")
        print(f"  Company: {result['metadata'].get('company', 'N/A')}")
        print(f"  Location: {result['metadata'].get('location', 'N/A')}")
        print(f"  Preview: {result['text'][:150]}...")
    
    # Example 5: Comparison
    print("\n5. COMPARISON CONTENT")
    print("-" * 60)
    
    comparison = generator.generate_comparison_content(
        item1="Data Scientist",
        item2="Data Engineer",
        source="jobs"
    )
    
    print(f"Comparison Preview:\n{comparison[:400]}...")

if __name__ == "__main__":
    main()
