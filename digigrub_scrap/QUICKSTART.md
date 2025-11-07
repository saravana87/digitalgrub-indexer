# Quick Start Guide

## 🚀 Setup in 3 Steps

### Step 1: Create PostgreSQL Database
```bash
sudo -u postgres psql -c "CREATE DATABASE news_scraper_db;"
sudo -u postgres psql -c "CREATE USER your_username WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE news_scraper_db TO your_username;"
```

### Step 2: Configure .env File
```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

Update with your credentials:
```
DB_HOST=localhost
DB_NAME=news_scraper_db
DB_USER=your_username
DB_PASSWORD=your_password
DB_PORT=5432
```

### Step 3: Run the Scraper
```bash
source scrap/bin/activate
python newsscrap.py
```

**That's it!** The table will be created automatically. ✅

---

## 📊 Verify Data

Connect to PostgreSQL:
```bash
psql -U your_username -d news_scraper_db
```

Check your articles:
```sql
-- Count articles
SELECT COUNT(*) FROM news_articles;

-- View recent articles
SELECT id, title, category, scraped_date, index_status 
FROM news_articles 
ORDER BY scraped_date DESC 
LIMIT 10;

-- Check for duplicates (should be 0)
SELECT content_hash, COUNT(*) 
FROM news_articles 
GROUP BY content_hash 
HAVING COUNT(*) > 1;
```

---

## 🔧 Troubleshooting

### Connection Error
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify credentials in `.env` file
- Test connection: `psql -U your_username -d news_scraper_db`

### Table Not Created
- Check console output for errors
- Ensure user has CREATE TABLE privileges
- Manually grant: `GRANT ALL ON DATABASE news_scraper_db TO your_username;`

### Import Error: dotenv
- Activate virtual environment: `source scrap/bin/activate`
- Reinstall: `pip install python-dotenv`

---

## 📝 What Happens on First Run?

1. ✅ Loads database credentials from `.env`
2. ✅ Connects to PostgreSQL
3. ✅ Creates `news_articles` table (if not exists)
4. ✅ Creates indexes for performance
5. ✅ Scrapes articles from Vikatan
6. ✅ Generates SHA-256 hash for each article
7. ✅ Saves to database (or updates if duplicate)

---

## 🎯 Next Steps

- Modify `base_url` in `newsscrap.py` to scrape different categories
- Update the limit `article_links[:5]` to scrape more articles
- Set up a cron job for automatic scraping
- Build an indexing service using the `index_status` column

Happy scraping! 🎉
