# Add this to src/models.py to fix tags parsing

from typing import List, Optional, Union
import json

# Update the ContentResponse class
class ContentResponse(BaseModel):
    id: int
    source_id: int
    title: str
    description: Optional[str] = None
    content_url: Optional[str] = None
    content_text: Optional[str] = None
    published_at: Optional[datetime] = None
    thumbnail_url: Optional[str] = None
    author: Optional[str] = None
    tags: Optional[List[str]] = None
    engagement_metrics: Optional[dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @validator('tags', pre=True)
    def parse_tags(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            try:
                return json.loads(v)
            except:
                return []
        if isinstance(v, list):
            return v
        return []
    
    class Config:
        from_attributes = True
        extra = "ignore"
