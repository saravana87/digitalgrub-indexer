"""
Query database to find actual category and sector names
"""
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / "backend" / ".env"
load_dotenv(dotenv_path=env_path)

# Create database connection
db_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(db_url)

print("=" * 80)
print("Database Filter Values")
print("=" * 80)

# Get news categories
print("\n📰 NEWS CATEGORIES:")
with engine.connect() as conn:
    result = conn.execute(text("SELECT DISTINCT category FROM news_articles WHERE category IS NOT NULL ORDER BY category"))
    categories = [row[0] for row in result]
    for i, cat in enumerate(categories, 1):
        print(f"  {i:2d}. {cat}")
    print(f"\nTotal: {len(categories)} categories")

# Get news sources
print("\n📡 NEWS SOURCES:")
with engine.connect() as conn:
    result = conn.execute(text("SELECT DISTINCT source FROM news_articles WHERE source IS NOT NULL ORDER BY source"))
    sources = [row[0] for row in result]
    for i, src in enumerate(sources, 1):
        print(f"  {i:2d}. {src}")
    print(f"\nTotal: {len(sources)} sources")

# Get job sectors
print("\n💼 JOB SECTORS:")
with engine.connect() as conn:
    result = conn.execute(text("SELECT DISTINCT sector FROM jobs WHERE sector IS NOT NULL ORDER BY sector"))
    sectors = [row[0] for row in result]
    for i, sec in enumerate(sectors, 1):
        print(f"  {i:2d}. {sec}")
    print(f"\nTotal: {len(sectors)} sectors")

# Count records
print("\n📊 RECORD COUNTS:")
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM news_articles"))
    news_count = result.fetchone()[0]
    print(f"  News Articles: {news_count:,}")
    
    result = conn.execute(text("SELECT COUNT(*) FROM jobs"))
    jobs_count = result.fetchone()[0]
    print(f"  Job Postings:  {jobs_count:,}")

# Check what vector tables exist
print("\n🔍 VECTOR TABLES IN DATABASE:")
with engine.connect() as conn:
    result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE '%vector%' ORDER BY table_name"))
    tables = [row[0] for row in result]
    for table in tables:
        result2 = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
        count = result2.fetchone()[0]
        print(f"  {table}: {count:,} records")

print("\n" + "=" * 80)
