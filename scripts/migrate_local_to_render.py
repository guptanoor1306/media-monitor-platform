import sqlite3
import psycopg2
import os
from urllib.parse import urlparse

def migrate_sqlite_to_postgres():
    # Local SQLite
    sqlite_conn = sqlite3.connect('media_monitor.db')
    sqlite_conn.row_factory = sqlite3.Row
    
    # Get Render PostgreSQL URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found. Run this script on Render or set the env var.")
        return
    
    # Parse PostgreSQL URL
    url = urlparse(database_url)
    pg_conn = psycopg2.connect(
        host=url.hostname,
        port=url.port,
        database=url.path[1:],
        user=url.username,
        password=url.password
    )
    
    try:
        # Migrate sources
        sqlite_cursor = sqlite_conn.execute("SELECT * FROM sources")
        sources = sqlite_cursor.fetchall()
        
        pg_cursor = pg_conn.cursor()
        for source in sources:
            pg_cursor.execute("""
                INSERT INTO sources (id, name, url, source_type, is_active, description, 
                                   created_at, updated_at, last_scraped_at, scrape_frequency)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, tuple(source))
        
        # Migrate content
        sqlite_cursor = sqlite_conn.execute("SELECT * FROM contents")
        contents = sqlite_cursor.fetchall()
        
        for content in contents:
            pg_cursor.execute("""
                INSERT INTO contents (id, title, description, content_url, source_id, 
                                    author, published_at, tags, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, tuple(content))
        
        pg_conn.commit()
        print(f"✅ Migrated {len(sources)} sources and {len(contents)} content items!")
        
    except Exception as e:
        print(f"❌ Migration error: {e}")
        pg_conn.rollback()
    finally:
        sqlite_conn.close()
        pg_conn.close()

if __name__ == "__main__":
    migrate_sqlite_to_postgres()
