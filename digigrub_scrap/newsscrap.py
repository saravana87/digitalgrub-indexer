import requests
from bs4 import BeautifulSoup
import psycopg2
from psycopg2 import Error
from datetime import datetime, timedelta
import hashlib
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_content_hash(content):
    """Generate SHA-256 hash of content"""
    if not content:
        content = ""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

# Database connection function
def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'news_scraper_db'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT', '5432')
        )
        return connection
    except Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

def create_table_if_not_exists(connection):
    """Create news_articles table if it doesn't exist"""
    try:
        cursor = connection.cursor()
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS news_articles (
            id SERIAL PRIMARY KEY,
            title VARCHAR(500) NOT NULL,
            url VARCHAR(1000) UNIQUE NOT NULL,
            content TEXT,
            content_hash VARCHAR(64) UNIQUE NOT NULL,
            category VARCHAR(100),
            source VARCHAR(100),
            scraped_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            index_status INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_news_url ON news_articles(url);
        CREATE INDEX IF NOT EXISTS idx_content_hash ON news_articles(content_hash);
        CREATE INDEX IF NOT EXISTS idx_index_status ON news_articles(index_status);
        CREATE INDEX IF NOT EXISTS idx_scraped_date ON news_articles(scraped_date);
        CREATE INDEX IF NOT EXISTS idx_source ON news_articles(source);
        """
        
        cursor.execute(create_table_query)
        connection.commit()
        cursor.close()
        print("✅ Table 'news_articles' is ready")
        
    except Error as e:
        print(f"❌ Error creating table: {e}")
        connection.rollback()

def insert_article(connection, title, url, content, category, source='vikatan'):
    """Insert article into database or update if hash/URL already exists"""
    try:
        cursor = connection.cursor()
        
        # Generate content hash
        content_hash = generate_content_hash(content)
        
        # Check if article with same hash already exists
        check_query = """
        SELECT id, url, title FROM news_articles 
        WHERE content_hash = %s OR url = %s;
        """
        cursor.execute(check_query, (content_hash, url))
        existing = cursor.fetchone()
        
        if existing:
            existing_id, existing_url, existing_title = existing
            
            # Update existing article
            update_query = """
            UPDATE news_articles 
            SET title = %s,
                url = %s,
                content = %s,
                category = %s,
                source = %s,
                scraped_date = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING id;
            """
            
            cursor.execute(update_query, (
                title,
                url,
                content,
                category,
                source,
                datetime.now(),
                existing_id
            ))
            
            article_id = cursor.fetchone()[0]
            connection.commit()
            cursor.close()
            
            print(f"🔄 Article updated in database (ID: {article_id}) - duplicate content detected")
            return article_id
        else:
            # Insert new article
            insert_query = """
            INSERT INTO news_articles (title, url, content, content_hash, category, source, scraped_date, index_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
            """
            
            cursor.execute(insert_query, (
                title,
                url,
                content,
                content_hash,
                category,
                source,
                datetime.now(),
                0  # default index_status
            ))
            
            article_id = cursor.fetchone()[0]
            connection.commit()
            cursor.close()
            
            print(f"✅ New article saved to database (ID: {article_id})")
            return article_id
        
    except Error as e:
        print(f"❌ Error inserting/updating article: {e}")
        connection.rollback()
        return None

def get_articles_from_api(category, offset=0, limit=50, timeout=30):
    """Fetch article URLs from Vikatan API with publish date"""
    api_url = f"https://www.vikatan.com/api/v1/collections/{category}"
    params = {
        "item-type": "story",
        "offset": offset,
        "limit": limit
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(api_url, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        
        articles = []
        if 'items' in data:
            for item in data['items']:
                if item.get('type') == 'story':
                    story = item.get('story', {})
                    article_url = story.get('url', '')
                    if article_url and not article_url.startswith('http'):
                        article_url = f"https://www.vikatan.com{article_url}"
                    
                    # Get publish date from API
                    published_at = story.get('published-at') or story.get('first-published-at')
                    print(f"🗓️  Article published at: {published_at}")
                    articles.append({
                        'url': article_url,
                        'published_at': published_at
                    })
        
        return articles
    except requests.exceptions.Timeout:
        print(f"❌ Timeout error fetching from API (waited {timeout}s)")
        return []
    except Exception as e:
        print(f"❌ Error fetching from API: {e}")
        return []


def scrape_article_content(url, timeout=15):
    """Scrape content from a single Vikatan article URL"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    try:
        article_res = requests.get(url, headers=headers, timeout=timeout)
        article_soup = BeautifulSoup(article_res.text, "lxml")
        
        # Get article title
        title_tag = article_soup.find("h1", class_="styles-m__headline__1uXyt")
        title = title_tag.text.strip() if title_tag else "No Title"
        
        # Extract article text from specific sections only
        paragraphs = []
        
        # Find all story-card sections
        story_cards = article_soup.select("section.styles-m__story-card__3w7kc")
        
        for story_card in story_cards:
            # Within each story card, find story-element-text divs
            text_elements = story_card.select("div.story-element-text")
            
            for text_element in text_elements:
                # Extract all <p> tags within this text element
                for p_tag in text_element.select("p"):
                    text = p_tag.get_text(strip=True)
                    # Filter out very short or empty paragraphs
                    if text and len(text) > 10:
                        paragraphs.append(text)
        
        article_text = "\n\n".join(paragraphs)
        
        return title, article_text
    except requests.exceptions.Timeout:
        print(f"❌ Timeout error scraping article (waited {timeout}s)")
        return None, None
    except Exception as e:
        print(f"❌ Error scraping article content: {e}")
        return None, None


def scrape_bbc_article_list(base_url="https://www.bbc.com/tamil/topics/c7zp5zgxggdt", timeout=15):
    """Scrape BBC Tamil article list"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    try:
        response = requests.get(base_url, headers=headers, timeout=timeout)
        soup = BeautifulSoup(response.text, "lxml")
        
        articles = []
        # Find all article links
        for li in soup.select("li.bbc-t44f9r"):
            link_tag = li.select_one("h2 a[href]")
            time_tag = li.select_one("time[datetime]")
            
            if link_tag:
                article_url = link_tag.get('href', '')
                if article_url and not article_url.startswith('http'):
                    article_url = f"https://www.bbc.com{article_url}"
                
                publish_date = None
                if time_tag:
                    datetime_str = time_tag.get('datetime', '')
                    try:
                        publish_date = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                    except:
                        pass
                
                articles.append({
                    'url': article_url,
                    'published_at': publish_date
                })
        
        return articles
    except requests.exceptions.Timeout:
        print(f"❌ Timeout error fetching BBC articles (waited {timeout}s)")
        return []
    except Exception as e:
        print(f"❌ Error fetching BBC articles: {e}")
        return []


def scrape_bbc_article_content(url, timeout=15):
    """Scrape content from BBC Tamil article"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    try:
        article_res = requests.get(url, headers=headers, timeout=timeout)
        article_soup = BeautifulSoup(article_res.text, "lxml")
        
        # Get article title
        title_tag = article_soup.select_one("h1.article-heading")
        title = title_tag.text.strip() if title_tag else "No Title"
        
        # Extract article text from main content - only <p> tags
        paragraphs = []
        main_content = article_soup.select_one("main[role='main']")
        
        if main_content:
            # Get all paragraph tags within main, excluding ads and other sections
            for p_tag in main_content.select("div[dir='ltr'] p.css-jlpguk"):
                text = p_tag.get_text(strip=True)
                if text and len(text) > 20:  # Filter out very short paragraphs
                    paragraphs.append(text)
        
        article_text = "\n\n".join(paragraphs)
        
        return title, article_text
    except requests.exceptions.Timeout:
        print(f"❌ Timeout error scraping BBC article (waited {timeout}s)")
        return None, None
    except Exception as e:
        print(f"❌ Error scraping BBC article content: {e}")
        return None, None


def scrape_category(connection, category, months=6):
    """Scrape articles from last N months using API pagination"""
    print(f"\n{'='*80}")
    print(f"📂 Scraping {category.upper()} category (Last {months} months)")
    print(f"{'='*80}\n")
    
    # Calculate cutoff date (6 months ago)
    cutoff_date = datetime.now() - timedelta(days=months * 30)
    print(f"📅 Only scraping articles published after: {cutoff_date.strftime('%Y-%m-%d')}\n")
    
    scraped_count = 0
    skipped_old = 0
    offset = 0
    limit = 19  # API default limit per request
    stop_scraping = False
    
    while not stop_scraping:
        print(f"\n📡 Fetching articles from API (offset: {offset}, limit: {limit})...")
        articles_data = get_articles_from_api(category, offset=offset, limit=limit)
        
        if not articles_data:
            print(f"⚠️  No more articles found at offset {offset}")
            break
        
        print(f"Found {len(articles_data)} article URLs from API")
        
        # Scrape each article
        for article_data in articles_data:
            url = article_data['url']
            published_at = article_data['published_at']
            
            # Parse publish date
            if published_at:
                try:
                    # Convert milliseconds timestamp to datetime
                    if isinstance(published_at, int):
                        publish_date = datetime.fromtimestamp(published_at / 1000)
                    else:
                        publish_date = datetime.fromisoformat(str(published_at).replace('Z', '+00:00'))
                    
                    # Check if article is older than cutoff date
                    if publish_date < cutoff_date:
                        skipped_old += 1
                        print(f"⏭️  Skipping old article from {publish_date.strftime('%Y-%m-%d')}: {url}")
                        
                        # If we're getting old articles, might be reaching the end
                        if skipped_old >= 10:  # If 10 consecutive old articles, stop
                            print(f"\n⚠️  Found {skipped_old} consecutive old articles. Stopping scrape.")
                            stop_scraping = True
                            break
                        continue
                    else:
                        skipped_old = 0  # Reset counter when we find a recent article
                        print(f"📅 Published: {publish_date.strftime('%Y-%m-%d %H:%M')}")
                        
                except Exception as e:
                    print(f"⚠️  Could not parse date: {published_at} - {e}")
            
            print(f"\nScraping [{scraped_count + 1}]: {url}")
            
            title, article_text = scrape_article_content(url)
            
            if not title or not article_text:
                print(f"⚠️  Skipping - No content found")
                continue
            
            print(f"📰 {title}")
            print(article_text[:300])  # print first 300 chars
            print("...")
            
            # Save to database with source='vikatan'
            result = insert_article(connection, title, url, article_text, category, source='vikatan')
            if result:
                scraped_count += 1
            print("-" * 80)
        
        if stop_scraping:
            break
        
        # Move to next page
        offset += limit
        
        # If we got fewer articles than requested, we've reached the end
        if len(articles_data) < limit:
            print(f"⚠️  Reached end of available articles")
            break
    
    print(f"\n✅ Successfully scraped {scraped_count} articles from {category} category (last {months} months)\n")


def scrape_bbc_tamil(connection, months=6):
    """Scrape BBC Tamil articles from last N months"""
    print(f"\n{'='*80}")
    print(f"📂 Scraping BBC TAMIL (Last {months} months)")
    print(f"{'='*80}\n")
    
    # Calculate cutoff date
    cutoff_date = datetime.now() - timedelta(days=months * 30)
    print(f"📅 Only scraping articles published after: {cutoff_date.strftime('%Y-%m-%d')}\n")
    
    scraped_count = 0
    
    print(f"\n📡 Fetching articles from BBC Tamil homepage...")
    articles_data = scrape_bbc_article_list()
    
    if not articles_data:
        print(f"⚠️  No articles found")
        return
    
    print(f"Found {len(articles_data)} article URLs from BBC\n")
    
    # Scrape each article
    for article_data in articles_data:
        url = article_data['url']
        published_at = article_data['published_at']
        
        # Check if article is older than cutoff date
        if published_at:
            if published_at < cutoff_date:
                print(f"⏭️  Skipping old article from {published_at.strftime('%Y-%m-%d')}: {url}")
                continue
            else:
                print(f"📅 Published: {published_at.strftime('%Y-%m-%d')}")
        
        print(f"\nScraping [{scraped_count + 1}]: {url}")
        
        title, article_text = scrape_bbc_article_content(url)
        
        if not title or not article_text:
            print(f"⚠️  Skipping - No content found")
            continue
        
        print(f"📰 {title}")
        print(article_text[:300])  # print first 300 chars
        print("...")
        
        # Save to database with source='bbc' and category='general'
        result = insert_article(connection, title, url, article_text, category='general', source='bbc')
        if result:
            scraped_count += 1
        print("-" * 80)
    
    print(f"\n✅ Successfully scraped {scraped_count} articles from BBC Tamil (last {months} months)\n")


# Main execution
if __name__ == "__main__":
    # Categories to scrape
    vikatan_categories = ["technology", "business"]
    
    # Set months to scrape (articles from last N months)
    MONTHS_TO_SCRAPE = int(os.getenv('MONTHS_TO_SCRAPE', 6))
    
    # Connect to database
    print("Connecting to database...")
    db_connection = get_db_connection()
    
    if not db_connection:
        print("Failed to connect to database. Exiting...")
        exit(1)
    
    print("✅ Database connected successfully!\n")
    
    # Create table if not exists
    create_table_if_not_exists(db_connection)
    
    # Scrape Vikatan categories (last 6 months only)
    print("\n🌐 Starting Vikatan scraping...")
    for category in vikatan_categories:
        scrape_category(db_connection, category, months=MONTHS_TO_SCRAPE)
    
    # Scrape BBC Tamil (last 6 months only)
    print("\n🌐 Starting BBC Tamil scraping...")
    scrape_bbc_tamil(db_connection, months=MONTHS_TO_SCRAPE)
    
    # Close database connection
    if db_connection:
        db_connection.close()
        print("\n" + "="*80)
        print("✅ All sources scraped successfully!")
        print("✅ Database connection closed.")
        print("="*80)
