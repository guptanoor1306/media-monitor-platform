#!/usr/bin/env python3
"""
Real-time scraping script for frequent updates
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

async def main():
    """Main real-time scraping function"""
    print(f"🚀 Real-time scrape started at {datetime.now()}")
    
    try:
        results = await run_premium_scrape()
        total_items = sum(results.values())
        
        if total_items > 0:
            print(f"✅ Real-time update: {total_items} new items added")
            
            # Show successful sources
            successful = [(name, count) for name, count in results.items() if count > 0]
            for name, count in successful:
                print(f"  📰 {name}: {count} items")
        else:
            print("ℹ️ No new content found in this update cycle")
        
        return total_items
        
    except Exception as e:
        print(f"❌ Real-time scrape failed: {str(e)}")
        return 0

if __name__ == "__main__":
    asyncio.run(main())
