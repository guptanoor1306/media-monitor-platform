#!/usr/bin/env python3
"""
Real content scraping script for Media Monitor Platform
Scrapes actual content from RSS feeds, APIs, and web sources
"""

import asyncio
import aiohttp
import feedparser
import sys
import os
from datetime import datetime, timezone
from urllib.parse import urljoin
import re

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import SessionLocal, init_db
from src.models import Source, Content

# RSS feed URLs for major sources (using reliable working feeds)
RSS_FEEDS = {
    # Tech/Business Blogs  
    'TechCrunch': 'http://feeds.feedburner.com/TechCrunch/',
    'Hacker News': 'https://hnrss.org/frontpage',
    'The Verge': 'http://www.theverge.com/rss/index.xml',
    'Wired': 'http://feeds.wired.com/wired/index',
    'MIT Technology Review': 'http://feeds.technologyreview.com/technology_review_latest',
    'Ars Technica': 'http://feeds.arstechnica.com/arstechnica/index',
}

# Podcast RSS feeds (using reliable feeds)
PODCAST_FEEDS = {
    'How I Built This': 'http://feeds.npr.org/510313/podcast.xml',
    'The Tim Ferriss Show': 'http://feeds.feedburner.com/thetimferrissshow',
}

async def fetch_rss_content(session, name, url):
    """Fetch and parse RSS content from a URL"""
    try:
        print(f"📡 Fetching RSS feed for {name}...")
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
            if response.status == 200:
                content = await response.text()
                feed = feedparser.parse(content)
                
                if feed.bozo:
                    print(f"⚠️  Warning: RSS feed for {name} has parsing issues")
                
                return feed
            else:
                print(f"❌ Failed to fetch {name}: HTTP {response.status}")
                return None
    except Exception as e:
        print(f"❌ Error fetching {name}: {str(e)}")
        return None

def clean_text(text):
    """Clean HTML tags and normalize text"""
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Limit length
    return text[:500] + "..." if len(text) > 500 else text

def get_source_by_name(db, name):
    """Get source from database by name"""
    return db.query(Source).filter(Source.name.ilike(f"%{name}%")).first()

async def scrape_rss_feeds(db):
    """Scrape all RSS feeds and save content to database"""
    connector = aiohttp.TCPConnector(ssl=False)  # Disable SSL verification
    async with aiohttp.ClientSession(connector=connector) as session:
        all_feeds = {**RSS_FEEDS, **PODCAST_FEEDS}
        
        for source_name, feed_url in all_feeds.items():
            # Find the source in database
            source = get_source_by_name(db, source_name)
            if not source:
                print(f"⚠️  Source '{source_name}' not found in database, skipping...")
                continue
            
            feed = await fetch_rss_content(session, source_name, feed_url)
            if not feed or not feed.entries:
                continue
            
            print(f"📰 Processing {len(feed.entries)} items from {source_name}")
            
            for entry in feed.entries[:10]:  # Limit to 10 most recent items
                try:
                    # Extract basic info
                    title = entry.get('title', 'No Title')
                    link = entry.get('link', '')
                    
                    # Get description/summary
                    description = (
                        entry.get('summary', '') or 
                        entry.get('description', '') or
                        entry.get('content', [{}])[0].get('value', '') if entry.get('content') else ''
                    )
                    description = clean_text(description)
                    
                    # Get publish date
                    published_at = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        published_at = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
                    
                    # Get author
                    author = (
                        entry.get('author', '') or
                        feed.feed.get('title', source_name)
                    )
                    
                    # Check if content already exists
                    existing = db.query(Content).filter(
                        Content.source_id == source.id,
                        Content.title == title
                    ).first()
                    
                    if existing:
                        continue  # Skip duplicates
                    
                    # Create new content
                    content = Content(
                        source_id=source.id,
                        title=title,
                        description=description,
                        content_url=link,
                        published_at=published_at,
                        author=author,
                        tags=[source.source_type, 'RSS Feed'],
                        engagement_metrics={'source': 'RSS'},
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    
                    db.add(content)
                    
                except Exception as e:
                    print(f"❌ Error processing entry from {source_name}: {str(e)}")
                    continue
            
            # Commit after each source
            try:
                db.commit()
                print(f"✅ Saved content from {source_name}")
            except Exception as e:
                print(f"❌ Error saving content from {source_name}: {str(e)}")
                db.rollback()

async def scrape_reddit_posts():
    """Scrape Reddit posts using public API (no auth needed for reading)"""
    reddit_subs = [
        'Entrepreneur', 'startups', 'technology', 'investing', 
        'artificial', 'cryptocurrency', 'business', 'economics',
        'venturecapital', 'consulting'
    ]
    
    db = SessionLocal()
    
    connector = aiohttp.TCPConnector(ssl=False)  # Disable SSL verification
    async with aiohttp.ClientSession(connector=connector) as session:
        for sub in reddit_subs:
            try:
                source = get_source_by_name(db, f"Reddit - r/{sub}")
                if not source:
                    continue
                
                print(f"📱 Fetching Reddit posts from r/{sub}")
                url = f"https://www.reddit.com/r/{sub}/hot.json?limit=25"
                
                async with session.get(url, headers={'User-Agent': 'MediaMonitor/1.0'}) as response:
                    if response.status == 200:
                        data = await response.json()
                        posts = data.get('data', {}).get('children', [])
                        
                        for post_data in posts:
                            post = post_data.get('data', {})
                            
                            # Skip pinned/stickied posts
                            if post.get('stickied') or post.get('pinned'):
                                continue
                            
                            title = post.get('title', '')
                            text = post.get('selftext', '')
                            url = f"https://reddit.com{post.get('permalink', '')}"
                            author = f"u/{post.get('author', 'unknown')}"
                            
                            # Get engagement metrics
                            upvotes = post.get('ups', 0)
                            comments = post.get('num_comments', 0)
                            
                            # Only include posts with decent engagement
                            if upvotes < 50:
                                continue
                            
                            # Check for duplicates
                            existing = db.query(Content).filter(
                                Content.source_id == source.id,
                                Content.title == title
                            ).first()
                            
                            if existing:
                                continue
                            
                            # Create content
                            content = Content(
                                source_id=source.id,
                                title=title,
                                description=clean_text(text),
                                content_url=url,
                                published_at=datetime.fromtimestamp(post.get('created_utc', 0), tz=timezone.utc),
                                author=author,
                                tags=['Reddit', sub, 'Social Media'],
                                engagement_metrics={
                                    'upvotes': upvotes,
                                    'comments': comments,
                                    'source': 'Reddit'
                                },
                                created_at=datetime.utcnow(),
                                updated_at=datetime.utcnow()
                            )
                            
                            db.add(content)
                        
                        db.commit()
                        print(f"✅ Saved Reddit posts from r/{sub}")
                        
            except Exception as e:
                print(f"❌ Error scraping r/{sub}: {str(e)}")
                db.rollback()
    
    db.close()

async def main():
    """Main scraping function"""
    print("🚀 Starting real content scraping...")
    
    # Initialize database
    init_db()
    db = SessionLocal()
    
    try:
        # Clear old content first (optional) - handle foreign key constraints
        print("🧹 Clearing old content...")
        from src.models import Summary
        db.query(Summary).delete()  # Delete summaries first
        db.query(Content).delete()  # Then delete content
        db.commit()
        
        # Scrape RSS feeds
        await scrape_rss_feeds(db)
        
        # Scrape Reddit (disabled for now due to SSL issues)
        # await scrape_reddit_posts()
        
        # Count results
        total_content = db.query(Content).count()
        print(f"\n🎉 Scraping complete! Added {total_content} real content items")
        
        # Show breakdown by source type
        total_sources = db.query(Source).count()
        print(f"📊 Total sources in database: {total_sources}")
        
    except Exception as e:
        print(f"❌ Error during scraping: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
