# DigitalGrub Indexer

LlamaIndex-powered content indexing and generation system for job portals. Efficiently index job listings, news, and other content from multiple sources using PostgreSQL + PgVector for semantic search and AI-powered blog generation.

## 🎯 Features

- **Multi-Source Indexing**: Index data from multiple tables (jobs, tnnews, aijobs, etc.)
- **Incremental Updates**: Only index new/updated records (efficient & cost-effective)
- **PgVector Integration**: Native PostgreSQL vector storage (no separate vector DB needed)
- **RAG-Powered Content Generation**: Generate blog posts, titles, and trend analysis
- **Flexible Embedding Models**: Support for OpenAI or local (HuggingFace) embeddings
- **Metadata Filtering**: Filter by company, location, sector, etc.

## 📋 What is Incremental Indexing?

**Incremental indexing** means only processing new or modified records instead of re-indexing everything:

- ✅ **Faster**: Skip already-indexed records
- ✅ **Cheaper**: Fewer API calls to embedding services
- ✅ **Real-time**: Keep index fresh as crawlers add new data

**Example:**
- Day 1: 1000 jobs → Index 1000 records
- Day 2: 50 new jobs → Only index 50 (not 1050)
- Day 3: 10 updated → Only reindex 10

## 🏗️ Architecture

```
PostgreSQL Database
├── jobs (structured data)           → llamaindex_embedding_jobs (vectors)
├── tnnews (structured data)         → llamaindex_embedding_tnnews (vectors)
└── aijobs (structured data)         → llamaindex_embedding_aijobs (vectors)
```

## 🚀 Setup

### 1. Prerequisites

- Python 3.11+
- PostgreSQL with PgVector extension
- Virtual environment (`.venv`)

### 2. Install PgVector Extension

```sql
-- Connect to your PostgreSQL database
CREATE EXTENSION IF NOT EXISTS vector;
```

### 3. Install Dependencies

```bash
# Activate virtual environment
.venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 4. Configure Environment

Copy `.env.example` to `.env` and update with your settings:

```bash
# Database (update with your actual credentials)
DB_HOST=20.244.82.149
DB_PORT=5432
DB_NAME=booksgrub_index_sources
DB_USER=postgres
DB_PASSWORD=your_password

# Embedding Provider: 'local' (free) or 'openai' (better quality)
EMBEDDING_PROVIDER=local

# If using OpenAI
OPENAI_API_KEY=sk-your-key-here

# Vector dimensions (384 for local, 1536 for OpenAI)
VECTOR_DIMENSION=384
```

### 5. Setup Database (One-Time Setup)

Run the automated setup script to install PgVector and run migrations:

```bash
python setup_db.py
```

This will:
1. Install the PgVector extension in PostgreSQL
2. Add `index_status`, `created_at`, and `updated_at` columns to your tables
3. Create indexes for better query performance

**Or manually:**

```bash
# Run migrations
python migrate.py

# Check migration status
python migrate.py current
```

## 📖 Usage

### Incremental Indexing (Recommended)

Run this regularly (e.g., daily cron job) to index only new records:

```python
python example_index.py
```

This will:
1. Find records where `index_status IS NULL` or `!= 'indexed'`
2. Convert them to embeddings
3. Store vectors in PgVector
4. Mark records as `indexed`

### Generate Content

```python
python example_query.py
```

Features:
- Generate blog titles
- Create full blog posts
- Analyze trends
- Compare jobs/topics
- Search similar content

### Force Full Reindex

Only use when needed (e.g., changing embedding model):

```python
python example_reindex.py
```

⚠️ This resets all `index_status` and reprocesses everything.

## 🎨 Content Generation Examples

### 1. Generate Blog Titles

```python
from query_engine import ContentGenerator

generator = ContentGenerator()

titles = generator.generate_blog_title(
    topic="AI Jobs in Healthcare",
    source="jobs",
    num_suggestions=5
)
```

### 2. Generate Full Blog Post

```python
blog = generator.generate_blog_content(
    title="Top 10 Remote Tech Jobs in 2025",
    source="jobs",
    word_count=1000,
    style="listicle"  # or 'informative', 'analytical'
)

print(blog['content'])
print(blog['tags'])
print(blog['summary'])
```

### 3. Trend Analysis

```python
trends = generator.generate_trend_analysis(
    topic="Data Science Salaries",
    source="jobs"
)
```

### 4. Compare Topics

```python
comparison = generator.generate_comparison_content(
    item1="Full Stack Developer",
    item2="Backend Developer",
    source="jobs"
)
```

## 🔧 Customization

### Add New Data Source

1. **Create Model** in `models.py`:

```python
class NewSource(Base):
    __tablename__ = 'newsource'
    
    # ... your columns ...
    index_status = Column(String(50))
    
    def to_document_text(self) -> str:
        # Convert to text for embedding
        pass
    
    def to_metadata(self) -> dict:
        # Extract metadata for filtering
        pass
```

2. **Create Indexer** in `indexer.py`:

```python
class NewSourceIndexer(BaseIndexer):
    def __init__(self):
        super().__init__(
            table_name="newsource",
            model_class=NewSource,
            collection_name="llamaindex_embedding_newsource"
        )
```

3. **Add to Query Engine** in `query_engine.py`:

```python
self.new_source_indexer = NewSourceIndexer()
self.new_source_index = self.new_source_indexer.get_index()
```

## 📊 Database Schema Notes

Your `jobs` table has these key columns for content generation:
- `title`, `description`, `skills` - Main content
- `company`, `location`, `sector` - Metadata for filtering
- `salary`, `experience` - Useful for trend analysis
- `index_status` - Tracks indexing state

## 🤔 Choosing Embedding Model

### Local (Free, Private)
```env
EMBEDDING_PROVIDER=local
LOCAL_EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
VECTOR_DIMENSION=384
```
- ✅ Free
- ✅ Private (runs locally)
- ⚠️ Requires GPU for faster processing
- ⚠️ Slightly lower quality than OpenAI

### OpenAI (Best Quality)
```env
EMBEDDING_PROVIDER=openai
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_API_KEY=sk-...
VECTOR_DIMENSION=1536
```
- ✅ Highest quality
- ✅ Fast API calls
- ⚠️ Costs money (~$0.02 per 1M tokens)
- ⚠️ Data sent to OpenAI

## 🔄 Workflow Integration

### After Your Crawler Runs

```python
# Your crawler adds new jobs to the database
# Then run:
from indexer import JobIndexer

indexer = JobIndexer()
stats = indexer.index_records(batch_size=100)

print(f"Indexed {stats['total_indexed']} new jobs")
```

### Scheduled Indexing (Cron/Task Scheduler)

```bash
# Run daily at 2 AM
0 2 * * * cd /path/to/digitalgrub-indexer && .venv/bin/python example_index.py
```

## 📝 Project Structure

```
digitalgrub-indexer/
├── .env                    # Your configuration
├── .env.example           # Template
├── requirements.txt       # Dependencies
├── config.py             # Settings management
├── models.py             # Database models
├── indexer.py            # Indexing logic
├── query_engine.py       # Content generation
├── example_index.py      # Incremental indexing example
├── example_query.py      # Content generation examples
└── example_reindex.py    # Full reindex example
```

## 🐛 Troubleshooting

### "No module named 'llama_index'"
```bash
pip install -r requirements.txt
```

### "Extension 'vector' does not exist"
```sql
CREATE EXTENSION vector;
```

### "No new records to index"
Check if `index_status` column exists and contains NULL values for new records.

### Memory issues with local embeddings
Reduce `batch_size` in indexing:
```python
indexer.index_records(batch_size=50)  # Default is 100
```

## 📚 Resources

- [LlamaIndex PgVector Docs](https://docs.llamaindex.ai/en/stable/examples/vector_stores/postgres/)
- [PgVector GitHub](https://github.com/pgvector/pgvector)
- [LlamaIndex RAG Guide](https://docs.llamaindex.ai/en/stable/getting_started/starter_example/)

## 🤝 Contributing

Feel free to extend this for your specific needs:
- Add more data sources
- Create custom prompt templates
- Implement metadata filters
- Add LLM provider options

## 📄 License

MIT License - Feel free to use in your projects!
