#!/usr/bin/env python3
"""
Daily scraper service that can be called via API endpoint
"""

import asyncio
import sys
import os
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.premium_scraper import run_premium_scrape
from src.database import SessionLocal
from src.models import Source, Content

async def run_daily_scrape():
    """Run daily scraping and return statistics."""
    print(f"🚀 Daily scrape started at {datetime.now()}")
    
    try:
        # Get current content count before scraping
        db = SessionLocal()
        content_before = db.query(Content).count()
        sources_before = db.query(Source).count()
        db.close()
        
        # Run the premium scraper
        results = await run_premium_scrape()
        total_new_items = sum(results.values())
        
        # Get counts after scraping
        db = SessionLocal()
        content_after = db.query(Content).count()
        sources_after = db.query(Source).count()
        db.close()
        
        # Calculate actual additions
        actual_new_content = content_after - content_before
        actual_new_sources = sources_after - sources_before
        
        stats = {
            "scrape_time": datetime.now().isoformat(),
            "content_before": content_before,
            "content_after": content_after,
            "new_content_added": actual_new_content,
            "sources_before": sources_before,
            "sources_after": sources_after,
            "new_sources_added": actual_new_sources,
            "successful_sources": {name: count for name, count in results.items() if count > 0},
            "total_scraped_items": total_new_items,
            "status": "success"
        }
        
        if actual_new_content > 0:
            print(f"✅ Daily scrape successful: {actual_new_content} new articles added")
            print(f"📊 Total content: {content_after} (+{actual_new_content})")
            print(f"📡 Total sources: {sources_after} (+{actual_new_sources})")
            
            # Show successful sources
            successful = [(name, count) for name, count in results.items() if count > 0]
            for name, count in successful:
                print(f"  📰 {name}: {count} items")
        else:
            print("ℹ️ No new content found in this scraping cycle")
            stats["status"] = "no_new_content"
        
        return stats
        
    except Exception as e:
        error_stats = {
            "scrape_time": datetime.now().isoformat(),
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }
        print(f"❌ Daily scrape failed: {str(e)}")
        return error_stats

def run_daily_scrape_sync():
    """Synchronous wrapper for the async scrape function."""
    return asyncio.run(run_daily_scrape())

if __name__ == "__main__":
    stats = run_daily_scrape_sync()
    print(f"📊 Final stats: {stats}")
