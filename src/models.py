from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel

# Create Base for SQLAlchemy models
Base = declarative_base()


class Source(Base):
    """Media source (blog, podcast, social media account, etc.)"""
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    source_type = Column(String(50), nullable=False)  # blog, podcast, twitter, reddit, etc.
    description = Column(Text)
    thumbnail_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    last_updated = Column(DateTime, default=datetime.utcnow)
    update_interval = Column(Integer, default=3600)  # seconds
    source_metadata = Column(JSON)  # Additional source-specific data
    
    # Relationships
    contents = relationship("Content", back_populates="source")
    user_sources = relationship("UserSource", back_populates="source")


class Content(Base):
    """Individual content item from a source"""
    __tablename__ = "contents"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    title = Column(String(500), nullable=False)
    description = Column(Text)
    content_url = Column(String(500))
    content_text = Column(Text)
    published_at = Column(DateTime)
    thumbnail_url = Column(String(500))
    author = Column(String(255))
    tags = Column(JSON)  # List of tags
    engagement_metrics = Column(JSON)  # Likes, shares, comments, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    source = relationship("Source", back_populates="contents")
    summaries = relationship("Summary", back_populates="content")


class Summary(Base):
    """AI-generated summary of content"""
    __tablename__ = "summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("contents.id"))
    prompt = Column(Text, nullable=False)
    summary_text = Column(Text, nullable=False)
    model_used = Column(String(100))
    tokens_used = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    content = relationship("Content", back_populates="summaries")


class User(Base):
    """User account"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user_sources = relationship("UserSource", back_populates="user")
    alerts = relationship("Alert", back_populates="user")
    scheduled_tasks = relationship("ScheduledTask", back_populates="user")


class UserSource(Base):
    """User's selected sources"""
    __tablename__ = "user_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    source_id = Column(Integer, ForeignKey("sources.id"))
    is_active = Column(Boolean, default=True)
    added_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="user_sources")
    source = relationship("Source", back_populates="user_sources")


class Alert(Base):
    """User-defined alerts for specific keywords/themes"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(255), nullable=False)
    keywords = Column(JSON, nullable=False)  # List of keywords to monitor
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_triggered = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="alerts")


class ScheduledTask(Base):
    """Scheduled monitoring tasks"""
    __tablename__ = "scheduled_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    source_ids = Column(JSON)  # List of source IDs to monitor
    prompt = Column(Text, nullable=False)
    schedule = Column(String(100), nullable=False)  # cron-like expression
    is_active = Column(Boolean, default=True)
    last_run = Column(DateTime)
    next_run = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="scheduled_tasks")


# Pydantic models for API
class SourceCreate(BaseModel):
    name: str
    url: str
    source_type: str
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    update_interval: Optional[int] = 3600
    source_metadata: Optional[dict] = None


class SourceResponse(BaseModel):
    id: int
    name: str
    url: str
    source_type: str
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_active: bool = True
    last_updated: Optional[datetime] = None
    update_interval: int = 3600
    source_metadata: Optional[dict] = None
    
    class Config:
        # Pydantic v1 syntax
        from_attributes = True
        # Allow extra fields from the database
        extra = "ignore"


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
    
    class Config:
        # Pydantic v1 syntax
        from_attributes = True
        # Allow extra fields from the database
        extra = "ignore"


class SummaryRequest(BaseModel):
    content_ids: List[int]
    prompt: str


class SummaryResponse(BaseModel):
    id: int
    content_id: int
    prompt: str
    summary_text: str
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        extra = "ignore"


class AlertCreate(BaseModel):
    name: str
    keywords: List[str]


class ScheduledTaskCreate(BaseModel):
    name: str
    description: Optional[str] = None
    source_ids: List[int]
    prompt: str
    schedule: str  # cron-like expression
