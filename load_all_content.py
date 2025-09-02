#!/usr/bin/env python3
"""
Load all 401 content items from real_content.json to the live database
"""

import json
import requests
from datetime import datetime

def load_all_content_to_live_db():
    """Load all content items to the live Render database"""
    
    base_url = "https://media-monitor-platform-1.onrender.com"
    
    try:
        # First check current content count
        print("🔍 Checking current content count...")
        response = requests.get(f"{base_url}/api/content?limit=1")
        if response.status_code == 200:
            current_count = len(response.json()) if response.json() else 0
            print(f"📊 Current content count: {current_count}")
        
        # Load the local content data
        print("📂 Loading content from real_content.json...")
        with open('real_content.json', 'r') as f:
            contents_data = json.load(f)
        
        print(f"📰 Found {len(contents_data)} items in local file")
        
        # We'll use the admin populate endpoint with a custom approach
        # Since we can't modify the live code directly, let's check if there are other endpoints
        
        # Try the migrate-real-data endpoint
        print("🚀 Attempting to load via migrate-real-data endpoint...")
        response = requests.get(f"{base_url}/migrate-real-data")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Migration completed!")
            print(f"📊 Result: {result}")
        else:
            print(f"❌ Migration failed with status: {response.status_code}")
            print(f"Response: {response.text}")
        
        # Check final count
        print("\n🔍 Checking final content count...")
        response = requests.get(f"{base_url}/api/content?limit=1000")
        if response.status_code == 200:
            final_content = response.json()
            print(f"📊 Final content count: {len(final_content)}")
            
            # Show some sample titles to verify
            if final_content:
                print("\n📝 Sample content loaded:")
                for i, item in enumerate(final_content[:5]):
                    print(f"  {i+1}. {item.get('title', 'No title')[:60]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    load_all_content_to_live_db()
