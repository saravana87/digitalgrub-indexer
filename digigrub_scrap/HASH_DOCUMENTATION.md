# Hash-Based Duplicate Prevention

## How It Works

The system uses **SHA-256 hashing** to prevent duplicate content from being stored in the database.

### Key Features:

1. **Content Hash Generation**: Every article's content is hashed using SHA-256
2. **Duplicate Detection**: Before inserting, the system checks if the hash or URL already exists
3. **Smart Updates**: If duplicate found, updates the existing record instead of creating new one

## Hash Column Details

- **Column Name**: `content_hash`
- **Type**: VARCHAR(64) - stores 64-character SHA-256 hash
- **Constraint**: UNIQUE - prevents duplicate content
- **Index**: Indexed for fast lookups

## Behavior

### Scenario 1: New Article
```
Content: "This is a new article..."
Hash: a3f5b2c1d4e6...
Action: ✅ INSERT new record
```

### Scenario 2: Same Content, Different URL
```
Content: "This is a new article..." (identical)
Hash: a3f5b2c1d4e6... (same hash)
Action: 🔄 UPDATE existing record with new URL
```

### Scenario 3: Same URL, Different Content
```
URL: https://example.com/article1 (same)
Content: "Updated article content..." (different)
Hash: f7e8d9c0b1a2... (different hash)
Action: 🔄 UPDATE existing record with new content and hash
```

### Scenario 4: Completely Duplicate
```
URL: https://example.com/article1 (same)
Content: "This is a new article..." (same)
Hash: a3f5b2c1d4e6... (same)
Action: 🔄 UPDATE with fresh scraped_date timestamp
```

## Database Queries

### Check for duplicates manually:
```sql
-- Find articles with duplicate content
SELECT content_hash, COUNT(*) as count 
FROM news_articles 
GROUP BY content_hash 
HAVING COUNT(*) > 1;

-- View article with specific hash
SELECT * FROM news_articles 
WHERE content_hash = 'your_hash_here';
```

### Update hash for specific article:
```python
import hashlib

content = "Your article content..."
hash_value = hashlib.sha256(content.encode('utf-8')).hexdigest()
print(hash_value)
```

## Migration for Existing Tables

If you already have a `news_articles` table without the `content_hash` column:

1. **Run the migration SQL**:
   ```bash
   psql -U your_username -d news_scraper_db -f migrate_add_hash.sql
   ```

2. **Generate hashes for existing records**:
   ```bash
   python update_hashes.py
   ```

This will:
- Add the `content_hash` column
- Create unique constraint and index
- Populate hashes for all existing articles

## Benefits

✅ **Prevents duplicate content** even with different URLs  
✅ **Saves storage space** by updating instead of duplicating  
✅ **Fast lookups** with indexed hash column  
✅ **Maintains data integrity** with unique constraints  
✅ **Tracks updates** with `updated_at` timestamp  

## Technical Details

- **Hash Algorithm**: SHA-256 (256-bit)
- **Hash Length**: 64 hexadecimal characters
- **Encoding**: UTF-8 before hashing
- **Collision Probability**: Virtually zero for practical purposes
