# DigitalGrub Portal - Backend

FastAPI backend for the DigitalGrub Content Management Portal.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
- Copy `.env` and update if needed
- Ensure `INDEXER_PATH` points to your digitalgrub-indexer folder

4. Run the server:
```bash
cd app
python main.py
```

Or with uvicorn directly:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## Endpoints

### Indexing
- `GET /api/v1/indexing/stats` - Get indexing statistics for all tables
- `GET /api/v1/indexing/dashboard` - Get dashboard statistics
- `GET /api/v1/indexing/crawlers` - Get crawler status

### Content Generation
- `POST /api/v1/content/search` - Search indexed content
- `POST /api/v1/content/generate-titles` - Generate blog titles
- `POST /api/v1/content/generate-blog` - Generate blog content

## Project Structure

```
backend/
├── app/
│   ├── api/              # API endpoints
│   │   ├── indexing.py   # Indexing stats endpoints
│   │   └── content.py    # Content generation endpoints
│   ├── core/             # Core configuration
│   │   ├── config.py     # Settings
│   │   └── database.py   # Database connection
│   ├── schemas/          # Pydantic models
│   │   ├── indexing.py   # Indexing schemas
│   │   └── content.py    # Content schemas
│   └── main.py           # FastAPI app
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables
```
