#!/usr/bin/env python3
"""
Enhanced scraping for major sources like Sequoia, BCG, McKinsey, a16z etc.
These are high-profile companies with public content that should be accessible.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from src.database import SessionLocal, engine
from src.models import Base, Source, Content
from src.services.content_aggregator import ContentAggregator
import asyncio
import time

# Create all tables
Base.metadata.create_all(bind=engine)

# Enhanced source configurations with better RSS feeds and endpoints
ENHANCED_SOURCES = {
    # VC & Investment Firms
    "a16z": {
        "name": "Andreessen Horowitz",
        "urls": [
            "https://a16z.com/feed/",
            "https://future.com/feed/",
            "https://a16z.com/tag/media/feed/"
        ],
        "type": "business_models"
    },
    "sequoia": {
        "name": "Sequoia Capital",
        "urls": [
            "https://www.sequoiacap.com/feed/",
            "https://medium.com/feed/sequoia-capital",
            "https://articles.sequoiacap.com/rss"
        ],
        "type": "business_models"
    },
    "bessemer": {
        "name": "Bessemer Venture Partners",
        "urls": [
            "https://www.bvp.com/feed",
            "https://www.bvp.com/atlas/feed",
            "https://medium.com/feed/@BVP"
        ],
        "type": "business_models"
    },
    "lightspeed": {
        "name": "Lightspeed Venture Partners",
        "urls": [
            "https://lsvp.com/feed/",
            "https://medium.com/feed/lightspeed-venture-partners"
        ],
        "type": "business_models"
    },
    
    # Consulting & Strategy
    "mckinsey": {
        "name": "McKinsey Digital",
        "urls": [
            "https://www.mckinsey.com/capabilities/mckinsey-digital/our-insights/rss",
            "https://www.mckinsey.com/industries/technology-media-and-telecommunications/our-insights/rss",
            "https://www.mckinsey.com/rss"
        ],
        "type": "business_models"
    },
    "bcg": {
        "name": "Boston Consulting Group",
        "urls": [
            "https://www.bcg.com/rss",
            "https://www.bcg.com/capabilities/digital-technology-data/overview/rss",
            "https://medium.com/feed/bcg-digital-ventures"
        ],
        "type": "business_models"
    },
    "bain": {
        "name": "Bain & Company",
        "urls": [
            "https://www.bain.com/rss/",
            "https://www.bain.com/insights/topics/technology/rss/"
        ],
        "type": "business_models"
    },
    
    # Media & Creator Specific
    "techcrunch_media": {
        "name": "TechCrunch Media",
        "urls": [
            "https://techcrunch.com/category/media-entertainment/feed/",
            "https://techcrunch.com/tag/creator-economy/feed/"
        ],
        "type": "media"
    },
    "bloomberg_media": {
        "name": "Bloomberg Media",
        "urls": [
            "https://www.bloomberg.com/feeds/podcasts/media.xml",
            "https://feeds.bloomberg.fm/BLM1178831946"
        ],
        "type": "media"
    },
    "reuters_media": {
        "name": "Reuters Media & Tech",
        "urls": [
            "https://feeds.reuters.com/reuters/technologyNews",
            "https://feeds.reuters.com/reuters/mediaNews"
        ],
        "type": "media"
    },
    
    # Creator Economy Specific
    "creator_economy_co": {
        "name": "Creator Economy Co",
        "urls": [
            "https://creatoreconomy.so/feed",
            "https://substack.com/feed/creator-economy"
        ],
        "type": "creator"
    },
    "passion_economy": {
        "name": "Passion Economy",
        "urls": [
            "https://li.substack.com/feed",
            "https://every.to/feed"
        ],
        "type": "creator"
    },
    
    # Podcasts
    "invest_like_best": {
        "name": "Invest Like the Best",
        "urls": [
            "https://feeds.simplecast.com/BqbsxVfO",
            "http://investlikethebest.libsyn.com/rss"
        ],
        "type": "podcasts"
    },
    "acquired": {
        "name": "Acquired Podcast",
        "urls": [
            "https://feeds.simplecast.com/WOeILCLy",
            "http://acquired.libsyn.com/rss"
        ],
        "type": "podcasts"
    }
}

async def update_source_with_better_feeds(source_name, config):
    """Update a source with better RSS feed URLs."""
    db = SessionLocal()
    try:
        # Find existing source or create new one
        source = db.query(Source).filter(Source.name.contains(source_name)).first()
        
        if not source:
            print(f"➕ Creating new source: {config['name']}")
            source = Source(
                name=config['name'],
                url=config['urls'][0],  # Use first URL as primary
                source_type=config['type'],
                description=f"Enhanced RSS feed for {config['name']}"
            )
            db.add(source)
            db.commit()
            db.refresh(source)
        else:
            print(f"🔄 Updating existing source: {source.name}")
            source.url = config['urls'][0]  # Update with better URL
            db.commit()
        
        return source
        
    finally:
        db.close()

async def scrape_enhanced_source(source, urls):
    """Try multiple URLs for a source until one works."""
    aggregator = ContentAggregator()
    
    for i, url in enumerate(urls):
        try:
            print(f"  🔗 Trying URL {i+1}/{len(urls)}: {url[:50]}...")
            
            # Temporarily update source URL
            original_url = source.url
            source.url = url
            
            new_content = await aggregator.scrape_source_safely(
                source,
                max_items=25,
                timeout=20
            )
            
            if new_content > 0:
                print(f"  ✅ Success! Scraped {new_content} items from {url[:50]}...")
                return new_content
            else:
                print(f"  ⚠️  No content from {url[:50]}...")
                
        except Exception as e:
            print(f"  ❌ Error with {url[:50]}...: {str(e)[:50]}")
            continue
        finally:
            # Restore original URL
            source.url = original_url
    
    print(f"  ❌ All URLs failed for {source.name}")
    return 0

async def main():
    print("🎯 ENHANCING MAJOR SOURCES")
    print("=" * 50)
    print("Adding better RSS feeds for Sequoia, BCG, McKinsey, a16z, etc.")
    
    total_new_content = 0
    successful_sources = 0
    
    for source_key, config in ENHANCED_SOURCES.items():
        print(f"\n🚀 Processing: {config['name']}")
        
        try:
            # Update or create source with better feeds
            source = await update_source_with_better_feeds(source_key, config)
            
            # Try scraping with multiple URLs
            new_content = await scrape_enhanced_source(source, config['urls'])
            
            if new_content > 0:
                total_new_content += new_content
                successful_sources += 1
                print(f"  🎉 {config['name']}: {new_content} new items!")
            else:
                print(f"  😞 {config['name']}: No content found")
                
        except Exception as e:
            print(f"  ❌ Error processing {config['name']}: {str(e)}")
        
        # Brief pause between sources
        await asyncio.sleep(2)
    
    print(f"\n🎉 ENHANCEMENT COMPLETE!")
    print(f"📊 Results:")
    print(f"  • Sources processed: {len(ENHANCED_SOURCES)}")
    print(f"  • Successful sources: {successful_sources}")
    print(f"  • Total new content: {total_new_content}")
    
    # Final verification
    print(f"\n🔍 Final verification...")
    db = SessionLocal()
    try:
        total_content = db.query(Content).count()
        total_sources = db.query(Source).count()
        print(f"📈 Database now contains:")
        print(f"  • Total content items: {total_content}")
        print(f"  • Total sources: {total_sources}")
        
        # Check content by bucket
        buckets = ['media', 'creator', 'business_models', 'podcasts']
        for bucket in buckets:
            bucket_sources = db.query(Source).filter(Source.source_type == bucket).all()
            bucket_content = 0
            working_sources = 0
            
            for source in bucket_sources:
                content_count = db.query(Content).filter(Content.source_id == source.id).count()
                bucket_content += content_count
                if content_count > 0:
                    working_sources += 1
            
            print(f"  📁 {bucket.upper()}: {bucket_content} items from {working_sources}/{len(bucket_sources)} sources")
            
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
