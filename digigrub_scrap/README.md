# News Scraper with PostgreSQL Database

## Setup Instructions

### 1. Install PostgreSQL (if not already installed)
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
```

### 2. Create Database and User
```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL prompt:
CREATE DATABASE news_scraper_db;
CREATE USER your_username WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE news_scraper_db TO your_username;
\q
```

### 3. Configure Environment Variables
Copy the example env file and update with your credentials:
```bash
cp .env.example .env
# Edit .env with your actual database credentials
```

Update `.env` file:
```bash
DB_HOST=localhost
DB_NAME=news_scraper_db
DB_USER=your_username
DB_PASSWORD=your_password
DB_PORT=5432
```

### 4. Run the Scraper
The script will automatically create the table if it doesn't exist:
```bash
source scrap/bin/activate
python newsscrap.py
```

**Note**: The table `news_articles` will be created automatically on first run!

## Database Schema

### Table: `news_articles`

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PRIMARY KEY | Auto-incrementing ID |
| `title` | VARCHAR(500) | Article headline |
| `url` | VARCHAR(1000) UNIQUE | Article URL (unique) |
| `content` | TEXT | Full article text |
| `content_hash` | VARCHAR(64) UNIQUE | SHA-256 hash of content (prevents duplicates) |
| `category` | VARCHAR(100) | Article category |
| `scraped_date` | TIMESTAMP | When article was scraped |
| `index_status` | INTEGER DEFAULT 0 | Indexing status (0=not indexed, 1=indexed, 2=failed) |
| `created_at` | TIMESTAMP | Record creation time |
| `updated_at` | TIMESTAMP | Last update time |

## Useful Queries

### View all articles
```sql
SELECT id, title, category, scraped_date, index_status FROM news_articles ORDER BY scraped_date DESC;
```

### Get articles not yet indexed
```sql
SELECT * FROM news_articles WHERE index_status = 0;
```

### Update index status
```sql
UPDATE news_articles SET index_status = 1 WHERE id = <article_id>;
```

### Count articles by category
```sql
SELECT category, COUNT(*) FROM news_articles GROUP BY category;
```

## Features

- ✅ Scrapes articles from Vikatan technology section
- ✅ Stores articles in PostgreSQL database
- ✅ **Automatic table creation** - no manual SQL needed!
- ✅ **Environment-based configuration** using .env file
- ✅ **SHA-256 hash for content to prevent duplicates**
- ✅ **Updates existing articles if duplicate hash or URL detected**
- ✅ Prevents duplicate articles using URL and content hash constraints
- ✅ Includes `index_status` column (default 0) for future indexing
- ✅ Proper error handling and logging
- ✅ Automatic duplicate detection and update mechanism

## Files Structure

```
newsscrap.py          # Main scraper script with table creation
.env                  # Database credentials (create from .env.example)
.env.example          # Template for environment variables
README.md             # This file
HASH_DOCUMENTATION.md # Detailed hash functionality documentation
```
