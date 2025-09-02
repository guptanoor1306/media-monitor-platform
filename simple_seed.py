import sqlite3
import json

# Get your content
conn = sqlite3.connect('media_monitor.db')
cursor = conn.execute("SELECT title, description, content_url FROM contents LIMIT 10") 
items = cursor.fetchall()

print("🎯 Your top content ready for live site:")
for i, (title, desc, url) in enumerate(items, 1):
    print(f"{i}. {title[:60]}...")

print(f"\n✅ {len(items)} items ready to make your site awesome!")
conn.close()
