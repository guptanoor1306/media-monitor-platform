import json
import os
from src.database import SessionLocal
from src.models import Source, Content
from datetime import datetime

def migrate_real_data():
    try:
        db = SessionLocal()
        
        # Clear existing sample data
        print("🗑️ Clearing sample data...")
        db.query(Content).delete()
        db.query(Source).delete()
        db.commit()
        
        # Load real sources
        print("📁 Loading real sources...")
        with open('real_sources.json', 'r') as f:
            sources_data = json.load(f)
            
        for source_data in sources_data:
            # Remove id to let database auto-generate
            source_data.pop('id', None)
            source = Source(**source_data)
            db.add(source)
        db.commit()
        
        # Load real content
        print("📁 Loading real content...")
        with open('real_content.json', 'r') as f:
            contents_data = json.load(f)
            
        for content_data in contents_data:
            # Remove id and fix foreign key
            content_data.pop('id', None)
            
            # Parse datetime strings if they exist
            for date_field in ['published_at', 'created_at', 'updated_at']:
                if content_data.get(date_field):
                    try:
                        content_data[date_field] = datetime.fromisoformat(content_data[date_field].replace('Z', '+00:00'))
                    except:
                        content_data[date_field] = datetime.now()
                        
            content = Content(**content_data)
            db.add(content)
        
        db.commit()
        db.close()
        
        print(f"✅ Migration complete! {len(sources_data)} sources, {len(contents_data)} content items")
        return {"sources": len(sources_data), "content": len(contents_data)}
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        db.rollback()
        return {"error": str(e)}

if __name__ == "__main__":
    migrate_real_data()
