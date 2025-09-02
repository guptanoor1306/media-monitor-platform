from typing import List, Dict, Any
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.models import Content

class ContentAggregator:
    def __init__(self):
        pass
    
    def search_content(self, query: str = "", limit: int = 50) -> List[Content]:
        """Search existing content in database"""
        try:
            db = SessionLocal()
            if query:
                contents = db.query(Content).filter(
                    Content.title.ilike(f"%{query}%")
                ).limit(limit).all()
            else:
                contents = db.query(Content).limit(limit).all()
            return contents
        except Exception as e:
            print(f"Search error: {e}")
            return []
        finally:
            db.close()
    
    def update_all_content(self) -> Dict[str, Any]:
        """Minimal implementation for deployment"""
        return {
            "message": "Update completed (scraping disabled for deployment)", 
            "results": {"minimal_mode": "Content loading from existing database"}
        }
