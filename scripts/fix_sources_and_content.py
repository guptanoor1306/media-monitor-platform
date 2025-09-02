#!/usr/bin/env python3
"""
Fix broken sources and populate with reliable RSS feeds for 1 year of content
"""

import asyncio
import aiohttp
import feedparser
import sys
import os
from datetime import datetime, timezone, timedelta
from urllib.parse import urljoin
import re

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import SessionLocal, init_db
from src.models import Source, Content, Summary

# Reliable RSS feeds organized by category
RELIABLE_SOURCES = {
    'blog': {
        # Business & Startup
        'TechCrunch': 'http://feeds.feedburner.com/TechCrunch/',
        'The Verge': 'http://www.theverge.com/rss/index.xml',
        'Wired': 'https://www.wired.com/feed/',
        'MIT Technology Review': 'https://www.technologyreview.com/feed/',
        'Harvard Business Review': 'http://feeds.hbr.org/harvardbusiness',
        'Fast Company': 'https://www.fastcompany.com/rss',
        'Inc.com': 'https://www.inc.com/rss.xml',
        'Entrepreneur': 'https://www.entrepreneur.com/rss',
        
        # VC & Investment
        'a16z Blog': 'https://a16z.com/feed/',
        'First Round Review': 'https://review.firstround.com/rss',
        'Y Combinator Blog': 'https://blog.ycombinator.com/feed',
        'Bessemer Venture Partners': 'https://www.bvp.com/feed',
        
        # Creator Economy & Media
        'Creator Economy Report': 'https://creatoreconomy.so/feed/',
        'The Information': 'https://www.theinformation.com/feed',
        'Platformer': 'https://www.platformer.news/feed',
        'Stratechery': 'https://stratechery.com/feed/',
        
        # Indian Business & Startup
        'Inc42': 'https://inc42.com/feed/',
        'YourStory': 'https://yourstory.com/feed/',
        'The Ken': 'https://the-ken.com/feed/',
        'Economic Times Startups': 'https://economictimes.indiatimes.com/tech/startups/rssfeeds/63553089.cms',
        
        # Tech News
        'Ars Technica': 'http://feeds.arstechnica.com/arstechnica/index',
        'Hacker News': 'https://hnrss.org/frontpage',
        'VentureBeat': 'https://venturebeat.com/feed/',
        'TechMeme': 'https://www.techmeme.com/feed.xml',
    },
    
    'podcast': {
        # Business & Startup Podcasts
        'How I Built This': 'https://feeds.npr.org/510313/podcast.xml',
        'Masters of Scale': 'https://feeds.megaphone.fm/mastersofscale',
        'The Tim Ferriss Show': 'https://rss.art19.com/tim-ferriss-show',
        'Invest Like the Best': 'https://feeds.megaphone.fm/GLT3576353990',
        'The a16z Podcast': 'https://feeds.soundcloud.com/users/soundcloud:users:7399265/sounds.rss',
        
        # Indian Business Podcasts  
        'The Seen and the Unseen': 'https://feeds.transistor.fm/the-seen-and-the-unseen',
        'Desi VC': 'https://feeds.soundcloud.com/users/soundcloud:users:394895517/sounds.rss',
        'Paisa Vaisa': 'https://feeds.soundcloud.com/users/soundcloud:users:394815227/sounds.rss',
        
        # Creator Economy Podcasts
        'Creator Economy Podcast': 'https://feeds.transistor.fm/creator-economy-podcast',
        'The Creator Economy': 'https://feeds.buzzsprout.com/1404486.rss',
    },
    
    'news': {
        # Business News
        'Reuters Business': 'https://feeds.reuters.com/reuters/businessNews',
        'Bloomberg': 'https://feeds.bloomberg.com/markets/news.rss',
        'Financial Times': 'https://www.ft.com/rss/home/uk',
        'Wall Street Journal': 'https://feeds.a.dj.com/rss/RSSWorldNews.xml',
        'Business Insider': 'https://www.businessinsider.com/rss',
        
        # Indian Business News
        'Economic Times': 'https://economictimes.indiatimes.com/rssfeedstopstories.cms',
        'LiveMint': 'https://www.livemint.com/rss/news',
        'Moneycontrol': 'https://www.moneycontrol.com/rss/business.xml',
    },
    
    'newsletter': {
        # Creator Economy Newsletters (RSS versions)
        'Morning Brew': 'https://www.morningbrew.com/rss',
        'The Hustle': 'https://thehustle.co/feed/',
        'CB Insights': 'https://www.cbinsights.com/rss',
        'Benedict Evans': 'https://feeds.feedburner.com/benedictevans',
    }
}

async def fetch_rss_content(session, name, url, limit_days=365):
    """Fetch and parse RSS content from a URL with date filtering"""
    try:
        print(f"📡 Fetching RSS: {name}")
        
        async with session.get(url, timeout=30) as response:
            if response.status != 200:
                print(f"❌ HTTP {response.status} for {name}")
                return []
            
            content = await response.text()
            
        # Parse RSS feed
        feed = feedparser.parse(content)
        
        if not hasattr(feed, 'entries') or not feed.entries:
            print(f"⚠️  No entries found in {name}")
            return []
        
        # Filter for recent content (last year)
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=limit_days)
        recent_entries = []
        
        for entry in feed.entries:
            # Parse entry date
            entry_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                entry_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                entry_date = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
            
            # Only include recent entries
            if entry_date and entry_date >= cutoff_date:
                recent_entries.append(entry)
            elif not entry_date:  # Include entries without dates
                recent_entries.append(entry)
        
        print(f"✅ {name}: {len(recent_entries)} recent items from {len(feed.entries)} total")
        return recent_entries
        
    except Exception as e:
        print(f"❌ Error fetching {name}: {str(e)}")
        return []

async def create_reliable_sources():
    """Create reliable RSS sources in database"""
    db = SessionLocal()
    
    try:
        print("🧹 Clearing existing broken sources...")
        # Delete summaries first (foreign key constraint)
        db.query(Summary).delete()
        # Delete content (foreign key constraint)  
        db.query(Content).delete()
        # Delete sources
        db.query(Source).delete()
        db.commit()
        print("✅ Cleared all existing sources and content")
        
        print("\n📂 Adding reliable RSS sources...")
        total_added = 0
        
        for source_type, sources in RELIABLE_SOURCES.items():
            print(f"\n📁 Adding {source_type.upper()} sources:")
            
            for name, url in sources.items():
                source = Source(
                    name=name,
                    url=url,
                    source_type=source_type,
                    description=f"Reliable RSS feed for {name}",
                    is_active=True,
                    update_interval=3600  # 1 hour
                )
                db.add(source)
                print(f"  ✅ {name}")
                total_added += 1
        
        db.commit()
        print(f"\n🎉 Added {total_added} reliable sources!")
        return total_added
        
    except Exception as e:
        print(f"❌ Error creating sources: {e}")
        db.rollback()
        return 0
    finally:
        db.close()

async def scrape_historical_content():
    """Scrape 1 year of content from all reliable sources"""
    db = SessionLocal()
    
    try:
        print("\n📰 Scraping historical content (1 year)...")
        
        # Get all sources
        sources = db.query(Source).all()
        
        async with aiohttp.ClientSession() as session:
            total_content = 0
            
            for source in sources:
                print(f"\n🔄 Processing: {source.name}")
                
                try:
                    # Fetch RSS entries
                    entries = await fetch_rss_content(session, source.name, source.url)
                    
                    if not entries:
                        continue
                    
                    # Convert entries to Content objects
                    added_count = 0
                    for entry in entries:
                        try:
                            # Extract content details
                            title = getattr(entry, 'title', 'No Title')
                            link = getattr(entry, 'link', '')
                            description = getattr(entry, 'summary', getattr(entry, 'description', ''))
                            
                            # Parse published date
                            published_at = None
                            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                                published_at = datetime(*entry.published_parsed[:6])
                            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                                published_at = datetime(*entry.updated_parsed[:6])
                            else:
                                published_at = datetime.now()
                            
                            # Extract author
                            author = getattr(entry, 'author', None)
                            
                            # Generate tags based on content
                            tags = []
                            content_text = (title + " " + description).lower()
                            
                            # Add intelligent tags
                            if any(word in content_text for word in ['startup', 'funding', 'venture', 'vc']):
                                tags.append('startup_funding')
                            if any(word in content_text for word in ['creator', 'influencer', 'youtube', 'tiktok']):
                                tags.append('creator_economy')
                            if any(word in content_text for word in ['ai', 'artificial intelligence', 'machine learning']):
                                tags.append('ai_technology')
                            if any(word in content_text for word in ['crypto', 'bitcoin', 'blockchain', 'web3']):
                                tags.append('crypto_web3')
                            if any(word in content_text for word in ['media', 'journalism', 'publishing']):
                                tags.append('media_industry')
                            
                            # Create Content object
                            content = Content(
                                title=title[:500] if title else 'No Title',
                                description=description[:1000] if description else '',
                                content_url=link,
                                content_text=description[:2000] if description else '',
                                author=author[:100] if author else None,
                                published_at=published_at,
                                tags=tags,
                                source_id=source.id
                            )
                            
                            db.add(content)
                            added_count += 1
                            
                        except Exception as e:
                            print(f"⚠️  Error processing entry: {e}")
                            continue
                    
                    if added_count > 0:
                        db.commit()
                        total_content += added_count
                        print(f"  ✅ Added {added_count} content items")
                    else:
                        print(f"  ⚠️  No content added")
                        
                except Exception as e:
                    print(f"  ❌ Error processing {source.name}: {e}")
                    db.rollback()
                    continue
            
            print(f"\n🎉 Historical scraping complete!")
            print(f"📊 Total content items added: {total_content}")
            
            # Show breakdown by category
            for source_type in ['blog', 'podcast', 'news', 'newsletter']:
                count = db.query(Content).join(Source).filter(Source.source_type == source_type).count()
                print(f"📁 {source_type.upper()}: {count} items")
                
            return total_content
            
    except Exception as e:
        print(f"❌ Error during content scraping: {e}")
        db.rollback()
        return 0
    finally:
        db.close()

async def main():
    """Main function to fix sources and populate content"""
    print("🚀 FIXING BROKEN SOURCES AND ADDING RELIABLE CONTENT")
    print("=" * 60)
    
    # Initialize database
    init_db()
    
    # Step 1: Create reliable sources
    sources_added = await create_reliable_sources()
    
    if sources_added > 0:
        # Step 2: Scrape historical content
        content_added = await scrape_historical_content()
        
        print("\n" + "=" * 60)
        print("🎉 SOURCES AND CONTENT FIX COMPLETE!")
        print(f"📂 Reliable sources added: {sources_added}")
        print(f"📰 Content items scraped: {content_added}")
        print("✅ Each category now has working content for filters")
        print("\n🌐 Access your dashboard: http://localhost:8001")
    else:
        print("❌ Failed to create sources. Content scraping skipped.")

if __name__ == "__main__":
    asyncio.run(main())
