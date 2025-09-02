#!/usr/bin/env python3
"""
Massive 6-month historical scraping for all sources to populate empty sources.
This script will scrape up to 6 months of content for sources that currently have 0 content.
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

def get_empty_sources():
    """Get sources that currently have no content."""
    db = SessionLocal()
    try:
        # Get all sources
        sources = db.query(Source).all()
        
        # Check which ones have no content
        empty_sources = []
        for source in sources:
            content_count = db.query(Content).filter(Content.source_id == source.id).count()
            if content_count == 0:
                empty_sources.append(source)
                
        print(f"📊 Found {len(empty_sources)} empty sources out of {len(sources)} total")
        return empty_sources
        
    finally:
        db.close()

async def scrape_source_historical(source, months_back=6):
    """Scrape historical content for a specific source."""
    print(f"\n🚀 Starting historical scrape for: {source.name}")
    print(f"   Type: {source.source_type}")
    print(f"   URL: {source.url}")
    
    try:
        aggregator = ContentAggregator()
        
        # Try to scrape with longer timeout for historical data
        new_content = await aggregator.scrape_source_safely(
            source, 
            max_items=100,  # More items for historical scraping
            timeout=30      # Longer timeout
        )
        
        if new_content > 0:
            print(f"✅ Successfully scraped {new_content} items from {source.name}")
            return new_content
        else:
            print(f"⚠️  No content found for {source.name}")
            return 0
            
    except Exception as e:
        print(f"❌ Error scraping {source.name}: {str(e)}")
        return 0

async def main():
    print("🎯 MASSIVE 6-MONTH HISTORICAL SCRAPING")
    print("=" * 50)
    print("This will populate all empty sources with historical content")
    
    # Get empty sources
    empty_sources = get_empty_sources()
    
    if not empty_sources:
        print("✅ All sources already have content!")
        return
    
    print(f"\n📋 Sources to scrape:")
    for source in empty_sources:
        print(f"  • {source.name} ({source.source_type})")
    
    print(f"\n🚀 Starting massive scraping operation...")
    
    total_scraped = 0
    successful_sources = 0
    
    # Process sources in batches to avoid overwhelming servers
    batch_size = 5
    for i in range(0, len(empty_sources), batch_size):
        batch = empty_sources[i:i + batch_size]
        print(f"\n📦 Processing batch {i//batch_size + 1}/{(len(empty_sources) + batch_size - 1)//batch_size}")
        
        # Process batch in parallel
        tasks = [scrape_source_historical(source) for source in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for source, result in zip(batch, results):
            if isinstance(result, Exception):
                print(f"❌ Error with {source.name}: {result}")
            elif result > 0:
                total_scraped += result
                successful_sources += 1
        
        # Brief pause between batches
        if i + batch_size < len(empty_sources):
            print("⏳ Pausing 5 seconds between batches...")
            await asyncio.sleep(5)
    
    print(f"\n🎉 HISTORICAL SCRAPING COMPLETE!")
    print(f"📊 Results:")
    print(f"  • Total items scraped: {total_scraped}")
    print(f"  • Sources with new content: {successful_sources}/{len(empty_sources)}")
    print(f"  • Success rate: {(successful_sources/len(empty_sources)*100):.1f}%")
    
    # Final verification
    print(f"\n🔍 Verifying results...")
    db = SessionLocal()
    try:
        total_content = db.query(Content).count()
        total_sources = db.query(Source).count()
        print(f"📈 Database now contains:")
        print(f"  • Total content items: {total_content}")
        print(f"  • Total sources: {total_sources}")
        
        # Check remaining empty sources
        remaining_empty = []
        for source in empty_sources:
            content_count = db.query(Content).filter(Content.source_id == source.id).count()
            if content_count == 0:
                remaining_empty.append(source.name)
        
        if remaining_empty:
            print(f"⚠️  Still empty sources: {len(remaining_empty)}")
            print(f"   {remaining_empty[:10]}...")
        else:
            print(f"🎉 All sources now have content!")
            
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
