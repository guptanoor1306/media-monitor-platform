import requests
import sqlite3
import json

# Get your local data
conn = sqlite3.connect('media_monitor.db')
conn.row_factory = sqlite3.Row

# Export sources
sources = []
for row in conn.execute("SELECT * FROM sources"):
    sources.append(dict(row))

# Export content  
contents = []
for row in conn.execute("SELECT * FROM contents LIMIT 50"):  # Start with 50 for testing
    contents.append(dict(row))

print(f"📊 Ready to migrate: {len(sources)} sources, {len(contents)} content items")

# Save to JSON files for manual upload
with open('sources_backup.json', 'w') as f:
    json.dump(sources, f, indent=2, default=str)
    
with open('contents_backup.json', 'w') as f:
    json.dump(contents, f, indent=2, default=str)

print("✅ Data exported to JSON files!")
print("📁 Files created: sources_backup.json, contents_backup.json")

conn.close()
