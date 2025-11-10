# Portal Backend - Quick Start

## Setup

1. **Activate virtual environment**
```powershell
.\.pvenv\Scripts\Activate.ps1
```

2. **Install dependencies**
```powershell
cd backend
pip install -r requirements.txt
```

## Test the Query Engine

```powershell
cd portal
python test_vector_search.py
```

This will:
- Connect to PgVector database
- List available filters (categories, sources, sectors)
- Generate blog titles with and without filters
- Show RAG in action!

## Start the Backend Server

```powershell
cd backend
python app/main.py
```

Server will start at: http://localhost:8000

API Documentation: http://localhost:8000/api/v1/docs

## API Endpoints

### 1. Get Filter Options
```http
GET /api/v1/content/filters
```

Response:
```json
{
  "news_categories": ["Technology", "Business", ...],
  "news_sources": ["TechCrunch", "Reuters", ...],
  "job_sectors": ["IT", "Healthcare", ...]
}
```

### 2. Generate Titles (Jobs)
```http
POST /api/v1/content/generate-titles
Content-Type: application/json

{
  "topic": "Software Developer Careers",
  "source_type": "jobs",
  "count": 5,
  "sector": "Technology"
}
```

### 3. Generate Titles (News)
```http
POST /api/v1/content/generate-titles
Content-Type: application/json

{
  "topic": "Industry Trends",
  "source_type": "news",
  "count": 5,
  "category": "Technology",
  "source": "TechCrunch"
}
```

Response:
```json
{
  "topic": "Software Developer Careers",
  "source_type": "jobs",
  "filters_applied": {
    "sector": "Technology"
  },
  "titles": [
    "Top 5 Skills Every Software Developer Needs in 2025",
    "How to Transition into a Tech Career: A Complete Guide",
    ...
  ]
}
```

## How It Works

### Without Filters
```
User Query → Embed Query → Search ALL vectors in PgVector → 
Top-10 Similar → Send to Azure OpenAI → Generate Titles
```

### With Filters
```
User Query + Filters → Apply Metadata Filter → 
Search FILTERED vectors in PgVector → 
Top-10 Similar (from filtered set) → Send to Azure OpenAI → Generate Titles
```

### Example Metadata Filter (Jobs with sector="Technology")
```sql
SELECT * FROM data_job_vector
WHERE metadata->>'sector' = 'Technology'
ORDER BY embedding <=> query_vector
LIMIT 10;
```

## Testing with cURL

### Get filters
```bash
curl http://localhost:8000/api/v1/content/filters
```

### Generate titles from jobs
```bash
curl -X POST http://localhost:8000/api/v1/content/generate-titles \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Data Science Careers",
    "source_type": "jobs",
    "count": 5,
    "sector": "Technology"
  }'
```

### Generate titles from news
```bash
curl -X POST http://localhost:8000/api/v1/content/generate-titles \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "AI Innovation",
    "source_type": "news",
    "count": 5,
    "category": "Technology"
  }'
```

## Next Steps

After confirming the backend works:
1. Update frontend to use new filter-based API
2. Add dropdowns for category/source/sector selection
3. Test end-to-end title generation with filters
