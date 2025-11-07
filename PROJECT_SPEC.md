# DigitalGrub Content Management Portal - Project Specification

**Version:** 1.0  
**Date:** November 6, 2025  
**Status:** Draft for Review

---

## 📋 Executive Summary

A React-based web portal for managing crawlers, monitoring indexing status, and generating AI-powered blog content using indexed job portal data. The portal enables content developers to create blog titles and articles automatically from structured data (jobs, news, AI jobs) using LlamaIndex + Azure OpenAI.

### Key Objectives
1. **Crawler Management**: Monitor and control crawler status/schedules
2. **Indexing Dashboard**: View indexing progress and data quality metrics
3. **Content Generation**: AI-powered blog creation with title suggestions
4. **Data Exploration**: Search and analyze indexed content

---

## 🏗️ Architecture Overview

### Technology Stack

#### Frontend
- **Framework**: React 18.3+ with TypeScript 5.6+
- **State Management**: TanStack Query v5 (React Query) + Zustand v5
- **UI Library**: Material-UI (MUI) v6 or Ant Design v5.21+
- **Routing**: React Router v6.28+
- **Data Fetching**: Axios 1.7+ with TanStack Query v5
- **Charts/Visualizations**: Recharts v2.13+ or Chart.js v4.4+
- **Code Editor**: Monaco Editor v0.52+ (for blog editing)
- **Build Tool**: Vite 6.0+
- **Styling**: Tailwind CSS v3.4+ + CSS Modules

#### Backend API
- **Framework**: FastAPI 0.115+ (Python 3.11+)
- **ASGI Server**: Uvicorn 0.32+ with uvloop
- **API Type**: RESTful JSON API
- **Authentication**: JWT tokens with refresh mechanism (python-jose 3.3+)
- **CORS**: Configured for React dev server + production domain
- **Validation**: Pydantic v2.9+
- **Documentation**: Auto-generated OpenAPI/Swagger UI

#### Database
- **Primary DB**: PostgreSQL 16+ with PgVector 0.8+ extension
- **ORM**: SQLAlchemy 2.0.35+ (existing models)
- **Connection Pool**: psycopg2-binary 2.9.10+ or asyncpg 0.30+ (async)
- **Migrations**: Alembic 1.14+ (existing setup)
- **Vector Storage**: PgVector 0.8+ (existing llamaindex_embedding_* tables)

#### AI/ML Services
- **Indexing**: LlamaIndex 0.12+ (existing)
- **Vector Store**: llama-index-vector-stores-postgres 0.3+
- **Azure Integration**: llama-index-embeddings-azure-openai 0.3+, llama-index-llms-azure-openai 0.3+
- **Embeddings**: Azure OpenAI text-embedding-3-large (3072-dim) (existing)
- **Content Generation**: Azure OpenAI GPT-4o/GPT-4-turbo (existing model-router)
- **Query Engine**: RAG with PgVector 0.8+ similarity search (existing)

#### Deployment
- **Frontend**: Vercel / Netlify / Azure Static Web Apps
- **Backend**: Azure App Service / Docker container
- **Database**: Existing PostgreSQL (20.244.82.149:5432)
- **Reverse Proxy**: Nginx (optional, for production)

---

## 📐 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (Port 5173)                │
│  ┌─────────────┬─────────────┬──────────────┬─────────────┐ │
│  │  Dashboard  │  Crawlers   │   Indexing   │  Content    │ │
│  │   Home      │  Management │   Monitor    │  Generator  │ │
│  └─────────────┴─────────────┴──────────────┴─────────────┘ │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API (JSON)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│               FastAPI Backend (Port 8000)                    │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │ Crawler API  │ Indexing API │  Content Generation API  │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Existing Python Modules                                │ │
│  │  • indexer.py (JobIndexer, TNNewsIndexer, AIJobIndexer) │ │
│  │  • query_engine.py (ContentGenerator)                   │ │
│  │  • models.py (SQLAlchemy models)                        │ │
│  │  • config.py (Settings management)                      │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────────┘
                         │ SQLAlchemy
                         ▼
┌─────────────────────────────────────────────────────────────┐
│          PostgreSQL + PgVector (20.244.82.149)              │
│  ┌────────────┬────────────┬────────────────────────────┐   │
│  │  jobs      │  tnnews    │  aijobs                    │   │
│  │  (33 cols) │            │                            │   │
│  └────────────┴────────────┴────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Vector Tables (3072 dimensions)                     │   │
│  │  • llamaindex_embedding_jobs                         │   │
│  │  • llamaindex_embedding_tnnews                       │   │
│  │  • llamaindex_embedding_aijobs                       │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Azure OpenAI (Embeddings + LLM)                │
│  • text-embedding-3-large (3072-dim)                        │
│  • model-router deployment                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Feature Specifications

### 1. Dashboard (Home Page)

**Purpose**: Overview of system health and key metrics

**Features**:
- **System Stats Cards**:
  - Total indexed records (jobs, tnnews, aijobs)
  - Unindexed records count
  - Last indexing run timestamp
  - Active crawlers count
  
- **Recent Activity Timeline**:
  - Recent indexing operations
  - Blog posts created
  - Crawler runs
  
- **Quick Actions**:
  - "Index New Records" button
  - "Generate Blog Title" button
  - "View All Crawlers" link

- **Charts**:
  - Indexing trends (last 7/30 days)
  - Content sources distribution (pie chart)
  - Blog generation activity

**API Endpoints**:
```
GET /api/v1/dashboard/stats
GET /api/v1/dashboard/recent-activity
GET /api/v1/dashboard/trends
```

**Mockup Flow**:
```
┌──────────────────────────────────────────────┐
│  DigitalGrub Portal        [👤 Admin ▼]     │
├──────────────────────────────────────────────┤
│  📊 Overview Statistics                      │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐        │
│  │  12,547 │ │   234   │ │    3    │        │
│  │ Indexed │ │Unindexed│ │Crawlers │        │
│  └─────────┘ └─────────┘ └─────────┘        │
│                                              │
│  📈 Indexing Trend (Last 7 Days)             │
│  [Line Chart]                                │
│                                              │
│  🕒 Recent Activity                          │
│  • 2 min ago: Indexed 50 jobs               │
│  • 15 min ago: Generated blog "Top Tech..." │
│  • 1 hour ago: Crawler "jobs" completed     │
└──────────────────────────────────────────────┘
```

---

### 2. Crawler Management

**Purpose**: Monitor crawler status, view logs, and manage crawler configurations

**Features**:
- **Crawler List Table**:
  - Columns: Name, Status, Last Run, Next Run, Records Added, Actions
  - Status badges (Running, Idle, Failed, Scheduled)
  - Sortable and filterable
  
- **Crawler Details Page**:
  - Configuration display (source URL, schedule, target table)
  - Execution history with logs
  - Manual trigger button
  - Enable/disable toggle
  
- **Crawler Logs Viewer**:
  - Real-time log streaming (WebSocket)
  - Filter by level (INFO, ERROR, WARNING)
  - Download logs as file

**Database Schema** (new tables):
```sql
CREATE TABLE crawlers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    target_table VARCHAR(50) NOT NULL,  -- 'jobs', 'tnnews', 'aijobs'
    source_url TEXT,
    schedule_cron VARCHAR(50),
    is_enabled BOOLEAN DEFAULT true,
    last_run_at TIMESTAMP,
    last_status VARCHAR(20),  -- 'success', 'failed', 'running'
    records_added INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE crawler_logs (
    id SERIAL PRIMARY KEY,
    crawler_id INTEGER REFERENCES crawlers(id),
    run_started_at TIMESTAMP NOT NULL,
    run_completed_at TIMESTAMP,
    status VARCHAR(20),
    records_crawled INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    log_file_path TEXT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**API Endpoints**:
```
GET    /api/v1/crawlers                 # List all crawlers
GET    /api/v1/crawlers/{id}            # Get crawler details
POST   /api/v1/crawlers                 # Create new crawler
PUT    /api/v1/crawlers/{id}            # Update crawler
DELETE /api/v1/crawlers/{id}            # Delete crawler
POST   /api/v1/crawlers/{id}/trigger    # Manual trigger
GET    /api/v1/crawlers/{id}/logs       # Get crawler logs
WS     /ws/crawlers/{id}/logs           # Real-time log stream
```

**Mockup Flow**:
```
┌──────────────────────────────────────────────┐
│  Crawlers Management         [+ Add Crawler] │
├──────────────────────────────────────────────┤
│ Name       │Status │Last Run    │Records│⚙️  │
├────────────┼───────┼────────────┼───────┼────┤
│job-crawler │🟢 Idle│2 hours ago │  150  │▶️⚙️│
│news-crawler│🔵 Run │Just now    │   45  │⏸️⚙️│
│ai-crawler  │🔴 Fail│1 day ago   │    0  │▶️⚙️│
└──────────────────────────────────────────────┘

[Click on crawler name opens details page]
```

---

### 3. Indexing Monitor

**Purpose**: Track indexing progress and data quality

**Features**:
- **Indexing Status Dashboard**:
  - Progress bars for each data source (jobs, tnnews, aijobs)
  - Indexing queue size
  - Average indexing time per record
  - Error rate
  
- **Manual Indexing Controls**:
  - "Index All Sources" button
  - Source-specific indexing (jobs only, news only, etc.)
  - Batch size configuration
  - Re-index specific records (by ID range)
  
- **Indexing History Table**:
  - Timestamp, Source, Records Processed, Duration, Status
  - View details (which records indexed, any errors)
  
- **Data Quality Metrics**:
  - Records with missing embeddings
  - Records with incomplete metadata
  - Vector dimension validation
  - Duplicate detection

**Database Schema** (new table):
```sql
CREATE TABLE indexing_runs (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,  -- 'jobs', 'tnnews', 'aijobs'
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    status VARCHAR(20),  -- 'running', 'completed', 'failed'
    records_processed INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    batch_size INTEGER DEFAULT 100,
    duration_seconds INTEGER,
    error_message TEXT,
    triggered_by VARCHAR(100),  -- 'manual', 'scheduled', 'auto'
    created_at TIMESTAMP DEFAULT NOW()
);
```

**API Endpoints**:
```
GET    /api/v1/indexing/status              # Current indexing status
POST   /api/v1/indexing/trigger             # Start indexing
GET    /api/v1/indexing/history             # Indexing history
GET    /api/v1/indexing/queue               # Current queue
GET    /api/v1/indexing/quality-check       # Data quality metrics
POST   /api/v1/indexing/reindex             # Reindex specific records
```

**Mockup Flow**:
```
┌──────────────────────────────────────────────┐
│  Indexing Monitor           [🔄 Index Now]   │
├──────────────────────────────────────────────┤
│  📊 Current Status                           │
│  Jobs:    ████████░░ 80% (10,200/12,750)    │
│  News:    ██████████ 100% (5,400/5,400)     │
│  AI Jobs: ██░░░░░░░░ 20% (120/600)          │
│                                              │
│  ⚡ Quick Actions                            │
│  [Index Jobs Only] [Index All] [Re-index]   │
│                                              │
│  📜 Recent Indexing Runs                     │
│  • 2h ago: jobs (150 records, 2.3min) ✅    │
│  • 5h ago: tnnews (45 records, 1.1min) ✅   │
│  • 1d ago: aijobs (0 records) ❌ Error      │
└──────────────────────────────────────────────┘
```

---

### 4. Content Generator

**Purpose**: AI-powered blog creation from indexed data

#### 4.1 Blog Title Generator

**Features**:
- **Input Form**:
  - Topic/keyword input
  - Data source selection (jobs, tnnews, aijobs, or "All Sources")
  - Number of suggestions slider (3-10)
  - Style selector (SEO-focused, Creative, Professional, Catchy)
  
- **Results Display**:
  - List of generated titles with scores
  - "Copy" button for each title
  - "Use This Title" → Opens blog content generator
  - "Regenerate" button
  - "Save Favorite" option
  
- **History/Favorites**:
  - View previously generated titles
  - Save favorite titles for later

**API Endpoints**:
```
POST   /api/v1/content/generate-titles      # Generate blog titles
GET    /api/v1/content/title-history        # Title generation history
POST   /api/v1/content/save-favorite-title  # Save favorite title
```

**Mockup Flow**:
```
┌──────────────────────────────────────────────┐
│  Generate Blog Title                         │
├──────────────────────────────────────────────┤
│  Topic: [Remote Tech Jobs in 2025________]   │
│                                              │
│  Data Source: [Jobs ▼]                      │
│  Number of Suggestions: ●─────────○ 5        │
│  Style: [⚫ SEO-focused  ○ Creative  ○...]   │
│                                              │
│  [🎯 Generate Titles]                        │
│                                              │
│  📝 Generated Titles:                        │
│  ┌──────────────────────────────────────┐   │
│  │ 1. "Top 10 Remote Tech Jobs Hiring    │   │
│  │     in 2025" [Copy] [Use This]        │   │
│  │ 2. "Remote Work Revolution: Best..."  │   │
│  │ 3. "High-Paying Remote Tech Roles..." │   │
│  └──────────────────────────────────────┘   │
└──────────────────────────────────────────────┘
```

#### 4.2 Blog Content Generator

**Features**:
- **Input Form**:
  - Title input (can use generated title)
  - Data source selection
  - Word count target (500-3000)
  - Writing style (Informative, Listicle, Analytical, How-to)
  - Tone selector (Professional, Casual, Technical)
  - Optional metadata filters (location, company, sector, etc.)
  
- **Content Editor**:
  - Monaco Editor with Markdown support
  - Live preview panel (split view)
  - AI suggestions panel (show retrieved data snippets)
  - Insert data button (add specific job examples)
  
- **Generated Content Display**:
  - Full blog content with formatting
  - Automatically generated tags
  - Summary/excerpt
  - Word count
  - SEO score (basic analysis)
  
- **Actions**:
  - Copy to clipboard
  - Export as Markdown/HTML
  - Save draft
  - Publish (if CMS integration exists)
  - Regenerate sections

**Database Schema** (new table):
```sql
CREATE TABLE blog_posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    content_html TEXT,
    summary TEXT,
    tags TEXT[],
    data_source VARCHAR(50),  -- 'jobs', 'tnnews', 'aijobs', 'mixed'
    word_count INTEGER,
    style VARCHAR(50),
    status VARCHAR(20) DEFAULT 'draft',  -- 'draft', 'published'
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    published_at TIMESTAMP
);

CREATE TABLE generation_history (
    id SERIAL PRIMARY KEY,
    blog_post_id INTEGER REFERENCES blog_posts(id),
    generation_type VARCHAR(50),  -- 'title', 'content', 'section'
    input_params JSONB,
    model_used VARCHAR(100),
    tokens_used INTEGER,
    generation_time_seconds FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**API Endpoints**:
```
POST   /api/v1/content/generate-blog        # Generate full blog
POST   /api/v1/content/generate-section     # Regenerate specific section
GET    /api/v1/content/similar-content      # Search similar indexed content
POST   /api/v1/content/save-draft           # Save blog draft
GET    /api/v1/content/drafts               # List saved drafts
PUT    /api/v1/content/drafts/{id}          # Update draft
DELETE /api/v1/content/drafts/{id}          # Delete draft
POST   /api/v1/content/publish              # Publish blog
```

**Mockup Flow**:
```
┌──────────────────────────────────────────────┐
│  Generate Blog Content                       │
├──────────────────────────────────────────────┤
│  Title: [Top 10 Remote Tech Jobs 2025____]   │
│  Source: [Jobs ▼]  Words: [●────] 1000      │
│  Style: [Listicle ▼]  Tone: [Professional]  │
│                                              │
│  Filters (Optional):                         │
│  Location: [Any ▼]  Sector: [Tech ▼]        │
│                                              │
│  [🎨 Generate Blog]                          │
│                                              │
│  ┌─────────────────┬────────────────────┐   │
│  │ Editor          │ Preview            │   │
│  │                 │                    │   │
│  │ # Top 10 Remote │ [Rendered HTML]    │   │
│  │                 │                    │   │
│  │ [AI-generated   │                    │   │
│  │  content...]    │                    │   │
│  └─────────────────┴────────────────────┘   │
│                                              │
│  📊 Generated: 1,024 words | 8 tags          │
│  [💾 Save Draft] [📋 Copy] [📤 Export]       │
└──────────────────────────────────────────────┘
```

#### 4.3 Additional Content Tools

**Trend Analysis**:
- Analyze trends for specific topics
- Time-based filtering
- Regional variations
- Salary trends
- Skills demand analysis

**Content Comparison**:
- Compare two topics (e.g., "Data Scientist vs Data Engineer")
- Side-by-side comparison generator

**Smart Search**:
- Semantic search across indexed data
- Find similar jobs/news/content
- Filter by metadata

**API Endpoints**:
```
POST   /api/v1/content/trend-analysis       # Generate trend analysis
POST   /api/v1/content/compare              # Generate comparison
POST   /api/v1/content/search               # Semantic search
```

---

### 5. User Management (Phase 2)

**Features**:
- User authentication (login/logout)
- Role-based access control (Admin, Content Creator, Viewer)
- User profile management
- Activity audit logs

**Database Schema**:
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'content_creator',  -- 'admin', 'content_creator', 'viewer'
    is_active BOOLEAN DEFAULT true,
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100),
    resource_type VARCHAR(50),
    resource_id INTEGER,
    details JSONB,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT NOW()
);
```

**API Endpoints**:
```
POST   /api/v1/auth/login                   # User login
POST   /api/v1/auth/logout                  # User logout
POST   /api/v1/auth/refresh                 # Refresh JWT token
GET    /api/v1/users/me                     # Current user profile
GET    /api/v1/users                        # List users (admin only)
POST   /api/v1/users                        # Create user (admin only)
PUT    /api/v1/users/{id}                   # Update user
```

---

## 🗂️ Project Structure

### Monorepo Structure

```
digitalgrub-indexer/
├── backend/                          # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app entry
│   │   ├── config.py                # Settings (existing)
│   │   ├── models.py                # DB models (existing)
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py              # Dependencies (DB session, auth)
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── dashboard.py     # Dashboard endpoints
│   │   │       ├── crawlers.py      # Crawler management
│   │   │       ├── indexing.py      # Indexing endpoints
│   │   │       ├── content.py       # Content generation
│   │   │       └── auth.py          # Authentication (Phase 2)
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── crawler_service.py   # Crawler logic
│   │   │   ├── indexing_service.py  # Indexing logic (wraps existing)
│   │   │   └── content_service.py   # Content generation (wraps existing)
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── crawler.py           # Pydantic schemas
│   │   │   ├── indexing.py
│   │   │   └── content.py
│   │   └── websockets/
│   │       ├── __init__.py
│   │       └── crawler_logs.py      # WebSocket for logs
│   ├── indexer.py                   # Existing indexing code
│   ├── query_engine.py              # Existing query engine
│   ├── migrations/                  # Alembic migrations (existing)
│   ├── requirements.txt             # Python dependencies
│   └── .env                         # Environment variables (existing)
│
├── frontend/                         # React frontend
│   ├── public/
│   │   ├── favicon.ico
│   │   └── index.html
│   ├── src/
│   │   ├── main.tsx                 # Entry point
│   │   ├── App.tsx                  # Root component
│   │   ├── api/
│   │   │   ├── client.ts            # Axios instance
│   │   │   ├── dashboard.ts         # Dashboard API calls
│   │   │   ├── crawlers.ts
│   │   │   ├── indexing.ts
│   │   │   └── content.ts
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── AppLayout.tsx    # Main layout with sidebar
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── Header.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── StatsCard.tsx
│   │   │   │   ├── ActivityTimeline.tsx
│   │   │   │   └── TrendChart.tsx
│   │   │   ├── crawlers/
│   │   │   │   ├── CrawlerList.tsx
│   │   │   │   ├── CrawlerDetails.tsx
│   │   │   │   └── CrawlerLogs.tsx
│   │   │   ├── indexing/
│   │   │   │   ├── IndexingStatus.tsx
│   │   │   │   ├── IndexingHistory.tsx
│   │   │   │   └── QualityMetrics.tsx
│   │   │   ├── content/
│   │   │   │   ├── TitleGenerator.tsx
│   │   │   │   ├── BlogEditor.tsx
│   │   │   │   ├── ContentPreview.tsx
│   │   │   │   └── SavedDrafts.tsx
│   │   │   └── common/
│   │   │       ├── LoadingSpinner.tsx
│   │   │       ├── ErrorBoundary.tsx
│   │   │       └── ConfirmDialog.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Crawlers.tsx
│   │   │   ├── Indexing.tsx
│   │   │   ├── ContentGenerator.tsx
│   │   │   └── Login.tsx            # Phase 2
│   │   ├── hooks/
│   │   │   ├── useDashboard.ts      # React Query hooks
│   │   │   ├── useCrawlers.ts
│   │   │   ├── useIndexing.ts
│   │   │   └── useContent.ts
│   │   ├── store/
│   │   │   └── authStore.ts         # Zustand store (Phase 2)
│   │   ├── types/
│   │   │   ├── crawler.ts           # TypeScript types
│   │   │   ├── indexing.ts
│   │   │   └── content.ts
│   │   ├── utils/
│   │   │   ├── formatters.ts        # Date, number formatting
│   │   │   └── constants.ts
│   │   └── styles/
│   │       └── globals.css
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── .env.local                   # Frontend env vars
│
├── crawlers/                         # Crawler scripts (from developers)
│   ├── job_crawler.py
│   ├── news_crawler.py
│   ├── ai_job_crawler.py
│   └── requirements.txt
│
├── docs/
│   ├── API.md                       # API documentation
│   ├── DEPLOYMENT.md                # Deployment guide
│   └── DEVELOPMENT.md               # Development setup
│
├── scripts/
│   ├── seed_crawlers.py             # Seed initial crawler configs
│   └── backup_db.sh
│
├── README.md                        # Existing main README
├── PROJECT_SPEC.md                  # This document
└── docker-compose.yml               # For local development (optional)
```

---

## 🚀 Implementation Phases

### Phase 1: MVP (2-3 weeks)
**Goal**: Core functionality for content generation

**Backend**:
- ✅ FastAPI project setup with basic structure
- ✅ Wrap existing indexer.py and query_engine.py as services
- ✅ Implement Dashboard API (stats, activity)
- ✅ Implement Indexing API (trigger, status, history)
- ✅ Implement Content Generation API (titles, blog content)
- ✅ Add CORS middleware
- ✅ Create OpenAPI documentation

**Frontend**:
- ✅ React + TypeScript project with Vite
- ✅ Setup routing (React Router)
- ✅ Create layout with sidebar navigation
- ✅ Dashboard page with stats cards
- ✅ Indexing Monitor page with manual trigger
- ✅ Blog Title Generator page
- ✅ Blog Content Generator page with Monaco Editor
- ✅ API integration with React Query

**Database**:
- ✅ Create new tables: indexing_runs, blog_posts, generation_history
- ✅ Alembic migration for new tables

**Testing**:
- Basic manual testing
- Test content generation with sample data

**Deliverables**:
- Working portal accessible at http://localhost:5173
- Backend API at http://localhost:8000
- Ability to generate blog titles and content
- Ability to trigger indexing manually

---

### Phase 2: Crawler Management (1-2 weeks)
**Goal**: Integrate crawler management

**Backend**:
- ✅ Implement Crawler Management API
- ✅ WebSocket endpoint for real-time logs
- ✅ Crawler execution service
- ✅ Integration with crawler scripts from developers

**Frontend**:
- ✅ Crawler list page with status badges
- ✅ Crawler details page
- ✅ Real-time log viewer (WebSocket)
- ✅ Manual crawler trigger functionality

**Database**:
- ✅ Create tables: crawlers, crawler_logs
- ✅ Alembic migration

**Testing**:
- Test crawler triggers
- Test log streaming

**Deliverables**:
- Full crawler management interface
- Real-time monitoring of crawler execution

---

### Phase 3: Authentication & User Management (1 week)
**Goal**: Secure the portal with user authentication

**Backend**:
- ✅ JWT authentication implementation
- ✅ User management API
- ✅ Role-based access control middleware
- ✅ Audit logging

**Frontend**:
- ✅ Login page
- ✅ Authentication state management (Zustand)
- ✅ Protected routes
- ✅ User profile display

**Database**:
- ✅ Create tables: users, audit_logs
- ✅ Alembic migration

**Testing**:
- Test authentication flow
- Test authorization (different user roles)

**Deliverables**:
- Secure portal with login system
- Multi-user support

---

### Phase 4: Enhancements & Polish (1-2 weeks)
**Goal**: Improve UX and add advanced features

**Features**:
- Advanced content search/filter
- Trend analysis visualization
- Comparison tools
- Export functionality (PDF, Markdown, HTML)
- Batch blog generation
- Scheduled content generation
- Email notifications
- Dark mode theme
- Mobile responsive design

**Testing**:
- End-to-end testing
- Performance optimization
- Security audit

**Deliverables**:
- Production-ready portal
- Deployment documentation

---

## 🔌 API Specifications

### Base URL
```
Development: http://localhost:8000/api/v1
Production: https://api.digitalgrub.com/api/v1
```

### Authentication (Phase 3)
```
Authorization: Bearer <JWT_TOKEN>
```

### Common Response Format

**Success Response**:
```json
{
  "status": "success",
  "data": { ... },
  "message": "Operation completed successfully"
}
```

**Error Response**:
```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { ... }
  }
}
```

### Sample API Endpoints

#### Dashboard Stats
```
GET /api/v1/dashboard/stats

Response:
{
  "status": "success",
  "data": {
    "total_indexed": {
      "jobs": 12547,
      "tnnews": 5400,
      "aijobs": 600
    },
    "unindexed": {
      "jobs": 234,
      "tnnews": 0,
      "aijobs": 120
    },
    "last_indexing_run": "2025-11-06T10:30:00Z",
    "active_crawlers": 3
  }
}
```

#### Trigger Indexing
```
POST /api/v1/indexing/trigger

Request Body:
{
  "source": "jobs",  // or "tnnews", "aijobs", "all"
  "batch_size": 100,
  "force_reindex": false  // optional
}

Response:
{
  "status": "success",
  "data": {
    "run_id": 123,
    "status": "running",
    "started_at": "2025-11-06T11:00:00Z"
  }
}
```

#### Generate Blog Titles
```
POST /api/v1/content/generate-titles

Request Body:
{
  "topic": "Remote Tech Jobs in 2025",
  "source": "jobs",
  "num_suggestions": 5,
  "style": "seo_focused"
}

Response:
{
  "status": "success",
  "data": {
    "titles": [
      {
        "id": 1,
        "title": "Top 10 Remote Tech Jobs Hiring in 2025",
        "score": 0.95
      },
      {
        "id": 2,
        "title": "Remote Work Revolution: Best Tech Opportunities in 2025",
        "score": 0.92
      },
      ...
    ],
    "generation_time": 2.3
  }
}
```

#### Generate Blog Content
```
POST /api/v1/content/generate-blog

Request Body:
{
  "title": "Top 10 Remote Tech Jobs Hiring in 2025",
  "source": "jobs",
  "word_count": 1000,
  "style": "listicle",
  "tone": "professional",
  "filters": {
    "location": "Remote",
    "sector": "Technology"
  }
}

Response:
{
  "status": "success",
  "data": {
    "title": "Top 10 Remote Tech Jobs Hiring in 2025",
    "content": "# Top 10 Remote Tech Jobs...\n\n...",
    "content_html": "<h1>Top 10 Remote Tech Jobs...</h1>...",
    "summary": "Discover the most in-demand remote tech positions...",
    "tags": ["remote work", "tech jobs", "2025", "hiring"],
    "word_count": 1024,
    "generation_time": 8.5,
    "sources_used": 15
  }
}
```

---

## 🎨 UI/UX Design Guidelines

### Design System
- **Color Palette**:
  - Primary: #1976D2 (Blue)
  - Secondary: #DC004E (Pink)
  - Success: #4CAF50 (Green)
  - Warning: #FF9800 (Orange)
  - Error: #F44336 (Red)
  - Background: #F5F5F5 (Light Gray)
  - Surface: #FFFFFF (White)

- **Typography**:
  - Headings: Inter, sans-serif
  - Body: Roboto, sans-serif
  - Code: Fira Code, monospace

- **Spacing**: 8px base unit (8, 16, 24, 32, 40, 48, 64)

### Component Guidelines
- Use Material-UI or Ant Design components
- Consistent button styles (primary, secondary, outlined)
- Loading states for all async operations
- Empty states with helpful messages
- Error states with retry options
- Success notifications (toast/snackbar)

### Responsive Design
- Desktop-first approach
- Breakpoints:
  - Desktop: 1200px+
  - Tablet: 768px - 1199px
  - Mobile: < 768px

---

## 🔒 Security Considerations

### Authentication & Authorization
- JWT tokens with 1-hour expiry
- Refresh tokens with 7-day expiry
- Password hashing with bcrypt
- Role-based access control (RBAC)

### API Security
- Rate limiting (100 req/min per IP)
- Input validation with Pydantic
- SQL injection prevention (SQLAlchemy ORM)
- XSS prevention (sanitize user input)
- CORS configuration (whitelist frontend domain)

### Data Security
- Environment variables for secrets (.env)
- HTTPS only in production
- Database connection encryption (SSL)
- Audit logs for sensitive operations

### Azure OpenAI Security
- API key stored in environment variables
- Key rotation strategy
- Usage monitoring to prevent abuse

---

## 📊 Performance Requirements

### Backend
- API response time: < 500ms (95th percentile)
- Content generation: < 10s per blog post
- Indexing: 100 records/minute minimum
- Concurrent users: Support 50+ simultaneous users

### Frontend
- Initial page load: < 3s
- Time to Interactive (TTI): < 5s
- Lighthouse score: > 90
- Bundle size: < 500KB (gzipped)

### Database
- Query response time: < 100ms (simple queries)
- Vector search: < 2s (for 10K+ records)
- Connection pool: 10-20 connections

---

## 🧪 Testing Strategy

### Backend Testing
- Unit tests (pytest)
  - Service layer tests
  - Model tests
  - Utility function tests
  
- Integration tests
  - API endpoint tests
  - Database integration tests
  - LlamaIndex integration tests
  
- Load tests (Locust)
  - API load testing
  - Concurrent indexing tests

### Frontend Testing
- Unit tests (Vitest)
  - Component tests
  - Hook tests
  - Utility function tests
  
- Integration tests (React Testing Library)
  - Page tests
  - User flow tests
  
- End-to-end tests (Playwright/Cypress)
  - Critical user journeys
  - Authentication flow
  - Content generation flow

### Manual Testing
- Cross-browser testing (Chrome, Firefox, Safari)
- Mobile responsiveness testing
- Accessibility testing (WCAG 2.1 AA)

---

## 🚀 Deployment Strategy

### Development Environment
- Frontend: Vite dev server (http://localhost:5173)
- Backend: Uvicorn dev server (http://localhost:8000)
- Database: Existing PostgreSQL (20.244.82.149)

### Staging Environment
- Frontend: Vercel preview deployment
- Backend: Azure App Service (staging slot)
- Database: Same as production (with separate schema)

### Production Environment
- **Frontend**: 
  - Vercel / Netlify / Azure Static Web Apps
  - CDN for static assets
  - Custom domain (e.g., portal.digitalgrub.com)
  
- **Backend**:
  - Azure App Service (Linux, Python 3.11)
  - or Docker container on Azure Container Instances
  - Auto-scaling enabled
  - Custom domain (e.g., api.digitalgrub.com)
  
- **Database**:
  - Existing PostgreSQL (20.244.82.149)
  - Regular backups
  - Connection pooling (PgBouncer)

### CI/CD Pipeline
- **GitHub Actions**:
  - Run tests on PR
  - Build frontend on merge to main
  - Deploy backend to Azure
  - Deploy frontend to Vercel
  
- **Deployment Steps**:
  1. Run linter and type checks
  2. Run unit tests
  3. Build production bundle
  4. Deploy to staging
  5. Run smoke tests
  6. Deploy to production
  7. Send notification to team

---

## 📝 Environment Variables

### Backend (.env)
```env
# Database
DB_HOST=20.244.82.149
DB_PORT=5432
DB_NAME=booksgrub_index_sources
DB_USER=postgres
DB_PASSWORD=your_password

# Azure OpenAI
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://ennkantitham-resource.cognitiveservices.azure.com/
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large
AZURE_OPENAI_LLM_DEPLOYMENT=model-router
AZURE_OPENAI_API_VERSION=2024-08-01-preview

# Vector Settings
VECTOR_DIMENSION=3072
VECTOR_TABLE_PREFIX=llamaindex_embedding

# API Settings
API_V1_PREFIX=/api/v1
DEBUG=false
LOG_LEVEL=INFO

# Security (Phase 3)
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:5173,https://portal.digitalgrub.com
```

### Frontend (.env.local)
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_BASE_URL=ws://localhost:8000/ws
```

---

## 🐛 Error Handling

### Backend Error Codes
```
400 - Bad Request (invalid input)
401 - Unauthorized (missing/invalid token)
403 - Forbidden (insufficient permissions)
404 - Not Found (resource doesn't exist)
409 - Conflict (duplicate resource)
422 - Unprocessable Entity (validation error)
429 - Too Many Requests (rate limit exceeded)
500 - Internal Server Error
503 - Service Unavailable (maintenance mode)
```

### Frontend Error Handling
- Display user-friendly error messages
- Show toast notifications for errors
- Retry failed requests (with exponential backoff)
- Fallback UI for critical errors
- Error boundary for React component errors
- Log errors to console (dev) / monitoring service (prod)

---

## 📈 Monitoring & Observability

### Backend Monitoring
- Application logs (structured JSON logs)
- API metrics (request count, response time, error rate)
- Database query performance
- Azure OpenAI usage (token count, cost)
- System metrics (CPU, memory, disk)

### Frontend Monitoring
- Error tracking (Sentry / LogRocket)
- Performance monitoring (Web Vitals)
- User analytics (Google Analytics / Mixpanel)
- Session replay for debugging

### Alerts
- API error rate > 5%
- Response time > 2s (95th percentile)
- Database connection errors
- Disk space < 10%
- Crawler failures

---

## 🔄 Future Enhancements

### Short-term (Next 3-6 months)
- Scheduled blog generation (cron jobs)
- Email notifications for indexing/crawler status
- Multi-language support (i18n)
- Advanced search with filters
- Bulk operations (batch blog generation)
- Content calendar view
- SEO score analysis

### Medium-term (6-12 months)
- Integration with CMS (WordPress, Ghost, etc.)
- Social media auto-posting
- A/B testing for blog titles
- Analytics dashboard (blog performance)
- Content recommendations
- Collaborative editing (multiple users)
- Version control for blog posts

### Long-term (12+ months)
- Custom AI model fine-tuning
- Voice-to-blog (speech input)
- Image generation for blog posts
- Multi-tenant support (SaaS model)
- Mobile app (React Native)
- Browser extension for quick blog creation

---

## ✅ Success Metrics

### Technical Metrics
- API uptime: > 99.5%
- Average indexing time: < 5 seconds per record
- Blog generation success rate: > 95%
- Frontend load time: < 3 seconds

### Business Metrics
- Blog posts created per week
- Time saved vs manual content creation
- User satisfaction score
- Crawler reliability (success rate)

### User Engagement
- Daily active users
- Average session duration
- Blog drafts saved
- Feature adoption rate

---

## 📞 Support & Maintenance

### Documentation
- API documentation (auto-generated with FastAPI)
- User guide with screenshots
- Developer setup guide
- Troubleshooting guide

### Maintenance Windows
- Weekly: Database backups
- Monthly: Security updates
- Quarterly: Dependency updates

### Support Channels
- GitHub Issues (bug reports, feature requests)
- Internal Slack channel
- Email support

---

## 🎓 Learning Resources

### For Frontend Developers
- React Official Docs: https://react.dev
- TypeScript Handbook: https://www.typescriptlang.org/docs/
- React Query: https://tanstack.com/query/latest/docs/react/overview
- Material-UI: https://mui.com

### For Backend Developers
- FastAPI Docs: https://fastapi.tiangolo.com
- LlamaIndex Docs: https://docs.llamaindex.ai
- SQLAlchemy Docs: https://docs.sqlalchemy.org
- PgVector: https://github.com/pgvector/pgvector

---

## 📄 Appendix

### A. Database Schema Diagram
See separate `DATABASE_SCHEMA.md` document

### B. API Endpoint Reference
See separate `API_REFERENCE.md` document

### C. Wireframes & Mockups
See `wireframes/` directory

### D. Architecture Decision Records (ADR)
See `docs/adr/` directory

---

## 🤝 Team & Responsibilities

### Roles
- **Backend Developer**: FastAPI API development, LlamaIndex integration
- **Frontend Developer**: React UI development, state management
- **DevOps Engineer**: Deployment, CI/CD, monitoring
- **Content Developer**: User testing, content requirements, QA

### Communication
- Daily standups (async in Slack)
- Weekly sprint planning
- Bi-weekly sprint retrospectives

---

## 📅 Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| Phase 1 (MVP) | 2-3 weeks | Dashboard, Indexing, Content Generation |
| Phase 2 (Crawlers) | 1-2 weeks | Crawler Management, Real-time Logs |
| Phase 3 (Auth) | 1 week | User Authentication, RBAC |
| Phase 4 (Polish) | 1-2 weeks | Enhancements, Testing, Deployment |
| **Total** | **5-8 weeks** | Production-ready portal |

---

## ✍️ Document Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | Nov 6, 2025 | Initial specification | GitHub Copilot |

---

**End of Project Specification**

This document will be updated as requirements evolve and new features are planned. Please review and provide feedback before implementation begins.
