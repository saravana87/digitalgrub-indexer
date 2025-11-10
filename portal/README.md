# DigitalGrub Portal

Web portal for managing content generation and monitoring indexing status.

## Project Structure

```
portal/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/      # API endpoints
│   │   ├── core/     # Configuration
│   │   └── schemas/  # Pydantic models
│   ├── requirements.txt
│   └── .env
├── frontend/          # React + TypeScript frontend
│   ├── src/
│   │   ├── pages/    # Page components
│   │   ├── api/      # API client
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## Quick Start

### Backend

```bash
cd portal/backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python app/main.py
```

Backend runs on: http://localhost:8000

### Frontend

```bash
cd portal/frontend
npm install
npm run dev
```

Frontend runs on: http://localhost:5173

## Features

- ✅ Dashboard with indexing statistics
- ✅ Real-time progress monitoring
- ✅ AI-powered blog title generation
- ✅ AI-powered blog content generation
- ✅ Monaco editor for content editing
- ✅ RESTful API with FastAPI
- ✅ Responsive UI with Ant Design

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## Technologies

**Backend:**
- FastAPI
- SQLAlchemy
- LlamaIndex
- Azure OpenAI
- PostgreSQL + PgVector

**Frontend:**
- React 18.3+
- TypeScript 5.6+
- Ant Design 5.21+
- Vite 6.0+
- TanStack Query
- Monaco Editor
