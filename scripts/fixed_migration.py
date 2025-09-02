import json
from datetime import datetime
from src.database import SessionLocal
from src.models import Source, Content

def fixed_migrate():
    try:
        db = SessionLocal()
        
        # Clear existing data
        db.query(Content).delete()
        db.query(Source).delete()
        db.commit()
        
        # Add sources with proper datetime handling
        with open('real_sources.json', 'r') as f:
            sources_data = json.load(f)
            
        for source_data in sources_data:
            # Remove problematic fields and let database handle them
            clean_source = {
                'name': source_data.get('name'),
                'url': source_data.get('url'),
                'source_type': source_data.get('source_type'),
                'description': source_data.get('description'),
                'is_active': bool(source_data.get('is_active', 1)),
                'update_interval': source_data.get('update_interval', 3600)
            }
            source = Source(**clean_source)
            db.add(source)
        
        db.commit()
        print(f"✅ Added {len(sources_data)} sources")
        
        # Add content with fixed datetime
        with open('real_content.json', 'r') as f:
            contents_data = json.load(f)
            
        for content_data in contents_data[:50]:  # Start with first 50 items
            clean_content = {
                'title': content_data.get('title'),
                'description': content_data.get('description'),
                'content_url': content_data.get('content_url'),
                'source_id': content_data.get('source_id', 1),
                'author': content_data.get('author'),
                'published_at': datetime.now(),  # Use current time for simplicity
                'tags': content_data.get('tags')
            }
            content = Content(**clean_content)
            db.add(content)
            
        db.commit()
        db.close()
        
        print(f"✅ Added first 50 content items successfully!")
        return {"sources": len(sources_data), "content": 50}
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    fixed_migrate()
