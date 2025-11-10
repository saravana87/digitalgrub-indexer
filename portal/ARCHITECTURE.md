# Portal Backend Architecture - How It Actually Works

## Overview
The portal backend uses **LlamaIndex + PgVector** for semantic search and RAG (Retrieval-Augmented Generation). It doesn't just query regular tables - it performs **vector similarity search** on embedded content.

## The Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER REQUEST                               │
│  "Generate blog titles about 'Python Developer Jobs in Singapore'"  │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      PORTAL BACKEND (FastAPI)                        │
│                   /api/v1/content/generate-titles                    │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CONTENT GENERATOR (query_engine.py)               │
│                                                                       │
│  Step 1: Create Query Engine with Vector Index                       │
│  ┌───────────────────────────────────────────────────┐              │
│  │ JobIndexer → get_index() → VectorStoreIndex       │              │
│  │   ├─ Connects to PostgreSQL + PgVector            │              │
│  │   ├─ Uses PGVectorStore from LlamaIndex           │              │
│  │   └─ Points to 'data_job_vector' table            │              │
│  └───────────────────────────────────────────────────┘              │
│                                                                       │
│  Step 2: Vector Similarity Search (PgVector)                         │
│  ┌───────────────────────────────────────────────────┐              │
│  │ User Query: "Python Developer Jobs Singapore"     │              │
│  │      ↓                                              │              │
│  │ Azure OpenAI Embedding API                         │              │
│  │ (text-embedding-3-large)                           │              │
│  │      ↓                                              │              │
│  │ Query Vector: [0.123, -0.456, 0.789, ...]         │              │
│  │ (3072 dimensions)                                   │              │
│  │      ↓                                              │              │
│  │ PgVector Query:                                     │              │
│  │ SELECT *, embedding <=> query_vector AS distance   │              │
│  │ FROM data_job_vector                                │              │
│  │ ORDER BY distance                                   │              │
│  │ LIMIT 10;                                           │              │
│  │      ↓                                              │              │
│  │ Top 10 Most Similar Job Postings Retrieved         │              │
│  └───────────────────────────────────────────────────┘              │
│                                                                       │
│  Step 3: Send Context + Prompt to LLM                                │
│  ┌───────────────────────────────────────────────────┐              │
│  │ Prompt to Azure OpenAI (gpt-4o):                   │              │
│  │                                                     │              │
│  │ "Based on these job postings:                      │              │
│  │  1. Senior Python Developer - Singapore - $8K      │              │
│  │  2. Python Backend Engineer - Singapore - $7K      │              │
│  │  3. Full Stack Python Dev - Singapore - $9K        │              │
│  │  ... (7 more similar jobs)                         │              │
│  │                                                     │              │
│  │  Generate 5 blog titles about Python jobs..."      │              │
│  └───────────────────────────────────────────────────┘              │
│                                                                       │
│  Step 4: LLM Response                                                │
│  ┌───────────────────────────────────────────────────┐              │
│  │ 1. "Top 5 Python Developer Skills in Singapore"    │              │
│  │ 2. "Python Developer Salary Guide 2025"            │              │
│  │ 3. "How to Land a Python Job in Singapore"         │              │
│  │ 4. "Python vs Java: Which Pays More?"              │              │
│  │ 5. "Remote Python Jobs in Southeast Asia"          │              │
│  └───────────────────────────────────────────────────┘              │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      RETURN TO USER                                  │
│                    (React Frontend)                                  │
└─────────────────────────────────────────────────────────────────────┘
```

## Database Structure

### Regular Tables (SQLAlchemy Models)
```sql
-- Source data tables
jobs                    -- Job postings (indexed)
news_articles           -- News articles (indexed)  
tnnews                  -- TN News (indexed)
ai_jobs                 -- AI job postings (indexed)
```

### Vector Tables (PgVector)
```sql
-- Vector embeddings for semantic search
data_job_vector         -- Job embeddings (3072-dim vectors)
  ├─ id (PRIMARY KEY)
  ├─ embedding (vector(3072))  -- <-- PgVector column!
  ├─ text (TEXT)
  └─ metadata (JSONB)

data_tnnews_vector      -- News embeddings
  ├─ id
  ├─ embedding (vector(3072))
  ├─ text
  └─ metadata

data_aijobs_vector      -- AI job embeddings
  └─ ...similar structure
```

## How PgVector Works

### What is PgVector?
- PostgreSQL extension for vector similarity search
- Stores high-dimensional vectors (embeddings)
- Performs fast similarity search using specialized indexes

### Vector Similarity Operators
```sql
-- Cosine distance (most common for embeddings)
embedding <=> query_vector

-- L2 distance
embedding <-> query_vector

-- Inner product
embedding <#> query_vector
```

### Example Query LlamaIndex Runs
```sql
-- When you search for "Python Developer Jobs"
-- LlamaIndex does this behind the scenes:

-- 1. Convert query to embedding
SELECT embedding_function('Python Developer Jobs');
-- Returns: [0.123, -0.456, 0.789, ..., 0.321] (3072 numbers)

-- 2. Find similar vectors
SELECT 
    id,
    text,
    metadata,
    embedding <=> '[0.123,-0.456,0.789,...]' AS distance
FROM data_job_vector
ORDER BY distance ASC
LIMIT 10;

-- Returns the 10 most similar job postings!
```

## How LlamaIndex Integrates

### 1. Connection Setup (indexer.py)
```python
# In BaseIndexer._setup_vector_store()
vector_store = PGVectorStore.from_params(
    database=settings.database_name,
    host=settings.database_host,
    password=settings.database_password,
    port=settings.database_port,
    user=settings.database_user,
    table_name="data_job_vector",  # PgVector table
    embed_dim=3072,  # text-embedding-3-large dimension
)
```

### 2. Vector Index (query_engine.py)
```python
# ContentGenerator initializes indexes
self.job_indexer = JobIndexer()
self.job_index = self.job_indexer.get_index()

# This VectorStoreIndex is connected to PgVector!
# It can query the vector table directly
```

### 3. Retriever (Semantic Search)
```python
# When you call search_similar_content()
retriever = VectorIndexRetriever(
    index=self.job_index,
    similarity_top_k=10,  # Top 10 similar items
)

nodes = retriever.retrieve("Python Developer Jobs")
# LlamaIndex:
#  1. Embeds your query → vector
#  2. Queries PgVector table
#  3. Returns 10 most similar nodes
```

### 4. Query Engine (RAG)
```python
# When you call generate_blog_title() or generate_blog_content()
query_engine = RetrieverQueryEngine(retriever=retriever)

response = query_engine.query("Generate blog titles about Python jobs")
# LlamaIndex:
#  1. Retrieves similar content (vector search)
#  2. Constructs prompt with context
#  3. Sends to Azure OpenAI LLM
#  4. Returns AI-generated response grounded in your data
```

## API Endpoints Explained

### POST /api/v1/content/search
**Pure Vector Search** (no LLM)
- Input: Search query
- Process: Vector similarity search in PgVector
- Output: Top-k similar documents with scores
- Use case: Finding relevant source material

### POST /api/v1/content/generate-titles
**RAG (Retrieval-Augmented Generation)**
- Input: Topic
- Process:
  1. Vector search for relevant jobs/news
  2. Send context + prompt to Azure OpenAI
  3. LLM generates titles based on real data
- Output: List of blog titles
- Use case: Content ideation

### POST /api/v1/content/generate-blog
**RAG (Full Content Generation)**
- Input: Title, tone, length
- Process:
  1. Vector search for relevant content (top-15)
  2. Send context + detailed prompt to Azure OpenAI
  3. LLM writes full blog post with real data points
- Output: Complete blog post (markdown)
- Use case: Automated content creation

## Why This Architecture?

### ✅ Advantages
1. **Grounded in Real Data**: AI responses cite actual job postings/news
2. **Semantic Search**: Understands meaning, not just keywords
3. **Scalable**: PgVector handles millions of vectors efficiently
4. **Up-to-date**: As you index new content, searches improve
5. **No Hallucination**: LLM gets real context from your database

### 🔧 Components Used
- **PostgreSQL + PgVector**: Vector storage and similarity search
- **LlamaIndex**: Orchestrates RAG pipeline
- **Azure OpenAI**: 
  - `text-embedding-3-large`: Converts text → vectors
  - `gpt-4o`: Generates content with context
- **FastAPI**: REST API layer
- **SQLAlchemy**: ORM for regular tables

## Testing the Vector Search

### Check if PgVector is Working
```sql
-- Connect to PostgreSQL
psql -h 20.244.82.149 -U postgres -d LLM

-- Check PgVector extension
\dx

-- Check vector tables
\dt data_*_vector

-- View sample vectors
SELECT 
    id, 
    left(text, 100) as text_preview,
    metadata,
    array_length(embedding::numeric[], 1) as vector_dimensions
FROM data_job_vector
LIMIT 5;
```

### Test Similarity Search
```sql
-- Find jobs similar to "Python Developer"
-- First, you need a query vector (normally from embedding API)
-- This is just for demonstration

SELECT 
    id,
    text,
    metadata->>'title' as job_title,
    embedding <=> (
        SELECT embedding 
        FROM data_job_vector 
        WHERE metadata->>'title' ILIKE '%Python Developer%'
        LIMIT 1
    ) AS similarity
FROM data_job_vector
ORDER BY similarity
LIMIT 10;
```

## Common Questions

### Q: Where is the PgVector library imported?
**A:** It's in `llama_index.vector_stores.postgres`:
```python
from llama_index.vector_stores.postgres import PGVectorStore
```

### Q: Do I need to install pgvector separately?
**A:** The extension is already installed in your PostgreSQL (version 0.8.0). The Python package `pgvector` is in your requirements.

### Q: How are vectors created?
**A:** In `indexer.py`:
1. Text is chunked (SentenceSplitter)
2. Each chunk sent to Azure OpenAI embedding API
3. Resulting vector (3072 dimensions) stored in PgVector table
4. Happens during indexing: `python index_jobs_only.py`

### Q: Can I see the vector similarity scores?
**A:** Yes, modify the search endpoint to return scores:
```python
# In content.py search_content()
for result in all_results:
    print(f"Score: {result.get('score', 0)}")
    print(f"Text: {result['text'][:100]}")
```

## Next Steps

### To Use the Portal:
1. ✅ Backend dependencies installed
2. ✅ PgVector tables populated (1,840 news articles indexed)
3. ⏳ Start backend: `python portal/backend/app/main.py`
4. ⏳ Install frontend deps: `cd portal/frontend && npm install`
5. ⏳ Start frontend: `npm run dev`
6. ⏳ Visit: http://localhost:5173

### To Verify Vector Search:
```python
# Test in Python console
from query_engine import ContentGenerator

generator = ContentGenerator()

# Search for similar jobs
results = generator.search_similar_content(
    query="Python Developer Singapore",
    source="jobs",
    top_k=5
)

for r in results:
    print(f"Score: {r['score']:.4f}")
    print(f"Text: {r['text'][:200]}")
    print("---")
```

### To Monitor Queries:
Enable PostgreSQL query logging to see the actual vector similarity queries LlamaIndex generates.

---

**In summary**: The portal backend uses LlamaIndex to perform vector similarity search on PgVector tables, retrieves the most relevant content, and feeds it to Azure OpenAI for grounded AI content generation. It's RAG (Retrieval-Augmented Generation) in action! 🚀
