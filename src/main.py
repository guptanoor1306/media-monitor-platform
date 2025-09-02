from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uvicorn

from src.database import get_db, init_db
from src.models import (
    Source, Content, Summary, User, UserSource, Alert, ScheduledTask,
    SourceCreate, SourceResponse, ContentResponse, SummaryRequest, 
    SummaryResponse, AlertCreate, ScheduledTaskCreate
)
from src.services.content_aggregator_minimal import ContentAggregator
from src.services.summarizer_minimal import SummarizerService
from src.config import settings

# Initialize FastAPI app
app = FastAPI(
    title="Media Monitor Platform",
    description="Comprehensive media monitoring and intelligence platform",
    version="1.0.0"
)

# Initialize services
content_aggregator = ContentAggregator()
summarizer_service = SummarizerService()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    
    # Auto-populate data if database is empty (for production)
    try:
        from src.database import SessionLocal
        from src.models import Source, Content
        
        db = SessionLocal()
        source_count = db.query(Source).count()
        content_count = db.query(Content).count()
        
        if source_count == 0:
            print("🔄 Database is completely empty, running initial setup...")
            # Import and run the migration functions
            from scripts.fixed_migration import fixed_migrate
            from scripts.migrate_real_data import migrate_real_data
            
            try:
                # Populate sources and initial content (only if empty)
                print("📊 Loading sources and initial content...")
                result1 = fixed_migrate()
                
                # Load all content (only if needed)
                if result1.get("content") != "skipped":
                    print("📰 Loading content items...")
                    result2 = migrate_real_data()
                
                print("✅ Database setup completed!")
            except Exception as e:
                print(f"⚠️  Auto-population failed: {e}")
        else:
            print(f"✅ Database already populated: {source_count} sources, {content_count} content items")
            
        db.close()
    except Exception as e:
        print(f"⚠️  Startup database check failed: {e}")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Media Monitor Platform"}

# Daily scraping endpoint
@app.post("/api/scrape/daily")
async def trigger_daily_scrape():
    """Manually trigger daily scraping."""
    try:
        from src.daily_scraper import run_daily_scrape_sync
        print("🚀 Manual daily scrape triggered via API")
        
        # Run scraping synchronously to get results
        stats = run_daily_scrape_sync()
        print(f"✅ Daily scrape completed: {stats}")
        
        return {
            "status": "completed",
            "message": "Daily scraping completed successfully",
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Daily scrape failed: {e}")
        return {
            "status": "error", 
            "error": str(e),
            "error_type": type(e).__name__,
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/scrape/status")
async def scrape_status():
    """Get scraping statistics."""
    try:
        from src.database import SessionLocal
        from src.models import Source, Content
        
        db = SessionLocal()
        content_count = db.query(Content).count()
        source_count = db.query(Source).count()
        
        # Get recent content (last 24 hours)
        from datetime import datetime, timedelta
        yesterday = datetime.now() - timedelta(days=1)
        recent_content = db.query(Content).filter(Content.created_at >= yesterday).count()
        
        # Get most recent content items
        latest_content = db.query(Content).order_by(Content.created_at.desc()).limit(5).all()
        latest_items = [
            {
                "id": item.id,
                "title": item.title[:50] + "..." if len(item.title) > 50 else item.title,
                "created_at": item.created_at.isoformat() if item.created_at else "Unknown",
                "source_id": item.source_id
            }
            for item in latest_content
        ]
        
        db.close()
        
        return {
            "total_content": content_count,
            "total_sources": source_count,
            "recent_content_24h": recent_content,
            "latest_items": latest_items,
            "last_check": datetime.now().isoformat(),
            "status": "active"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/debug/content-sync")
async def debug_content_sync():
    """Debug endpoint to check content synchronization."""
    try:
        from src.database import SessionLocal
        from src.models import Source, Content
        
        db = SessionLocal()
        
        # Get comprehensive stats
        total_content = db.query(Content).count()
        total_sources = db.query(Source).count()
        
        # Get content by source
        from sqlalchemy import func
        content_by_source = db.query(
            Source.name, 
            func.count(Content.id).label('content_count')
        ).outerjoin(Content, Source.id == Content.source_id).group_by(Source.id, Source.name).all()
        
        # Get recent content (last 3 days)
        from datetime import datetime, timedelta
        three_days_ago = datetime.now() - timedelta(days=3)
        recent_items = db.query(Content).filter(Content.created_at >= three_days_ago).order_by(Content.created_at.desc()).limit(10).all()
        
        recent_list = [
            {
                "id": item.id,
                "title": item.title,
                "created_at": item.created_at.isoformat() if item.created_at else "Unknown",
                "source_id": item.source_id,
                "engagement_metrics": item.engagement_metrics
            }
            for item in recent_items
        ]
        
        db.close()
        
        return {
            "database_stats": {
                "total_content": total_content,
                "total_sources": total_sources,
                "content_by_source": [{"source": name, "count": count} for name, count in content_by_source]
            },
            "recent_content_3days": recent_list,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/debug/podcast-data")
async def debug_podcast_data():
    """Debug endpoint to check podcast data structure."""
    try:
        from src.database import SessionLocal
        from src.models import Source, Content
        
        db = SessionLocal()
        
        # Get podcast sources
        podcast_sources = db.query(Source).filter(Source.source_type == 'podcast').all()
        
        result = {
            "podcast_sources": [
                {
                    "id": s.id,
                    "name": s.name,
                    "source_type": s.source_type,
                    "url": s.url
                }
                for s in podcast_sources
            ],
            "sample_content": []
        }
        
        # Get sample content from podcast sources
        if podcast_sources:
            sample_content = db.query(Content).filter(
                Content.source_id.in_([s.id for s in podcast_sources])
            ).limit(5).all()
            
            result["sample_content"] = [
                {
                    "id": c.id,
                    "title": c.title[:50] + "..." if len(c.title) > 50 else c.title,
                    "source_id": c.source_id,
                    "engagement_metrics": c.engagement_metrics,
                    "content_url": c.content_url
                }
                for c in sample_content
            ]
        
        db.close()
        return result
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/debug/openai")
async def debug_openai():
    """Debug endpoint to check OpenAI configuration."""
    from src.config import settings
    import os
    
    debug_info = {
        "api_key_exists": bool(settings.openai_api_key),
        "api_key_length": len(settings.openai_api_key) if settings.openai_api_key else 0,
        "api_key_starts_with_sk": settings.openai_api_key.startswith('sk-') if settings.openai_api_key else False,
        "api_key_preview": settings.openai_api_key[:10] + "..." if settings.openai_api_key else "None",
        "model": settings.openai_model,
        "env_var_exists": bool(os.getenv("OPENAI_API_KEY")),
        "env_var_preview": os.getenv("OPENAI_API_KEY", "None")[:10] + "..." if os.getenv("OPENAI_API_KEY") else "None"
    }
    
    # Test OpenAI client initialization with the same logic as summarizer
    try:
        if settings.openai_api_key:
            # Use OpenAI v1.3.8 client style
            from openai import OpenAI
            client = OpenAI(api_key=settings.openai_api_key)
            debug_info["client_style"] = "v1.3.8_client"
            debug_info["openai_test"] = "✅ OpenAI v1.3.8 client initialized"
        else:
            debug_info["openai_test"] = "❌ No API key"
    except Exception as e:
        debug_info["openai_test"] = f"❌ Error: {str(e)}"
        debug_info["error_type"] = type(e).__name__
    
    # Test the actual summarizer service
    try:
        from src.services.summarizer_minimal import SummarizerService
        summarizer = SummarizerService()
        init_result = summarizer._init_client()
        debug_info["summarizer_init"] = "✅ Success" if init_result else "❌ Failed"
        debug_info["summarizer_client_type"] = "v1.3.8_client"
    except Exception as e:
        debug_info["summarizer_error"] = str(e)
    
    return debug_info

# API Endpoints

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Magazine dashboard page."""
    return templates.TemplateResponse("magazine_dashboard.html", {"request": request})

# Sources Management
@app.post("/api/sources", response_model=SourceResponse)
async def create_source(source: SourceCreate, db: Session = Depends(get_db)):
    """Create a new media source."""
    db_source = Source(**source.dict())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source

@app.get("/api/sources", response_model=List[SourceResponse])
async def get_sources(
    source_type: Optional[str] = Query(None, description="Filter by source type"),
    db: Session = Depends(get_db)
):
    """Get all media sources with optional filtering."""
    query = db.query(Source).filter(Source.is_active == True)
    if source_type:
        query = query.filter(Source.source_type == source_type)
    return query.all()

@app.get("/api/sources/{source_id}", response_model=SourceResponse)
async def get_source(source_id: int, db: Session = Depends(get_db)):
    """Get a specific media source."""
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source

@app.put("/api/sources/{source_id}", response_model=SourceResponse)
async def update_source(
    source_id: int, 
    source_update: SourceCreate, 
    db: Session = Depends(get_db)
):
    """Update a media source."""
    db_source = db.query(Source).filter(Source.id == source_id).first()
    if not db_source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    for field, value in source_update.dict().items():
        setattr(db_source, field, value)
    
    db.commit()
    db.refresh(db_source)
    return db_source

@app.delete("/api/sources/{source_id}")
async def delete_source(source_id: int, db: Session = Depends(get_db)):
    """Delete a media source (soft delete)."""
    db_source = db.query(Source).filter(Source.id == source_id).first()
    if not db_source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    db_source.is_active = False
    db.commit()
    return {"message": "Source deleted successfully"}

# Content Management
@app.get("/api/content", response_model=List[ContentResponse])
async def get_content(
    source_id: Optional[int] = Query(None, description="Filter by source ID"),
    limit: int = Query(500, description="Number of items to return"),
    offset: int = Query(0, description="Number of items to skip"),
    db: Session = Depends(get_db)
):
    """Get content with optional filtering and pagination."""
    query = db.query(Content)
    if source_id:
        query = query.filter(Content.source_id == source_id)
    
    query = query.order_by(Content.published_at.desc())
    query = query.offset(offset).limit(limit)
    
    return query.all()

@app.get("/api/content/creator", response_model=List[ContentResponse])
async def get_creator_content(
    limit: int = Query(50, description="Number of items to return"),
    db: Session = Depends(get_db)
):
    """Get creator economy and monetization content prioritized."""
    try:
        # Simple approach: get all content and filter in Python
        all_content = db.query(Content).order_by(Content.published_at.desc()).limit(200).all()
        
        creator_content = []
        other_content = []
        
        for item in all_content:
            tags = item.tags or []
            title = (item.title or "").lower()
            desc = (item.description or "").lower()
            
            # Check if it has creator tags or mentions
            is_creator = (
                "creator_monetization" in tags or
                "creator_economy" in tags or
                "creator" in title or
                "monetization" in title or
                "creator" in desc or
                "monetization" in desc
            )
            
            if is_creator:
                creator_content.append(item)
            else:
                other_content.append(item)
        
        # Return creator content first, up to limit
        result = creator_content[:limit]
        if len(result) < limit:
            result.extend(other_content[:limit - len(result)])
        
        return result[:limit]
        
    except Exception as e:
        print(f"Creator endpoint error: {e}")
        # Fallback to regular content
        return db.query(Content).order_by(Content.published_at.desc()).limit(limit).all()

@app.get("/api/content/search")
async def search_content(
    q: str = Query(..., description="Search query"),
    limit: int = Query(50, description="Number of results to return"),
    db: Session = Depends(get_db)
):
    """Search content across all sources."""
    contents = content_aggregator.search_content(q, limit=limit)
    return {"query": q, "results": contents, "count": len(contents)}

@app.get("/api/content/{content_id}", response_model=ContentResponse)
async def get_content_item(content_id: int, db: Session = Depends(get_db)):
    """Get a specific content item."""
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content

# Content Updates
@app.post("/api/content/update")
async def update_content():
    """Trigger content update from all sources."""
    try:
        results = content_aggregator.update_all_sources()
        return {"message": "Content update completed", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content update failed: {str(e)}")

@app.post("/api/content/update/{source_id}")
async def update_source_content(source_id: int, db: Session = Depends(get_db)):
    """Trigger content update from a specific source."""
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    try:
        count = content_aggregator._update_source_content(source, db)
        return {"message": f"Updated {count} content items from {source.name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Source update failed: {str(e)}")

@app.post("/api/sources/{source_id}/scrape")
async def scrape_source_realtime(source_id: int, db: Session = Depends(get_db)):
    """Real-time scraping for a specific source when selected."""
    try:
        source = db.query(Source).filter(Source.id == source_id).first()
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        
        # Import the premium scraper
        from .premium_scraper import PremiumMediaScraper
        
        # Create source data format for scraper
        source_data = {
            'url': source.url,
            'type': source.source_type,
            'category': source.source_metadata.get('category', 'general') if source.source_metadata else 'general',
            'description': source.description,
            'priority': 'high'
        }
        
        # Perform real-time scraping
        async with PremiumMediaScraper() as scraper:
            count = await scraper.scrape_premium_feed(source.name, source_data)
        
        # Update source timestamp  
        source.last_updated = datetime.utcnow()
        db.commit()
        
        return {
            "message": f"Real-time scrape completed for {source.name}",
            "items_added": count,
            "source": source.name,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Real-time scraping error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Real-time scraping failed: {str(e)}")

# Summarization
@app.post("/api/summarize", response_model=SummaryResponse)
async def summarize_content(request: SummaryRequest):
    """Generate AI summary of selected content."""
    try:
        # Filter out locked/premium content before summarization
        from src.database import SessionLocal
        from src.models import Content
        
        db = SessionLocal()
        try:
            # Get all requested content
            contents = db.query(Content).filter(Content.id.in_(request.content_ids)).all()
            
            # Filter out premium/restricted content
            filtered_ids = []
            excluded_count = 0
            
            for content in contents:
                engagement_metrics = content.engagement_metrics or {}
                is_premium = engagement_metrics.get('is_premium', False)
                requires_visit = engagement_metrics.get('requires_visit_source', False)
                
                # Check URL and description for premium indicators
                url = content.content_url or ''
                description = content.description or ''
                title = content.title or ''
                
                is_restricted = (
                    is_premium or requires_visit or
                    '/premium/' in url or '/subscriber/' in url or
                    'economictimes.indiatimes.com/prime/' in url or
                    'businessinsider.com/prime/' in url or
                    any(indicator in (title + description).lower() 
                        for indicator in ['paywall', 'subscription required', 'login required', 'members only'])
                )
                
                if not is_restricted:
                    filtered_ids.append(content.id)
                else:
                    excluded_count += 1
            
            if not filtered_ids:
                raise HTTPException(status_code=400, 
                    detail=f"All {len(request.content_ids)} selected articles are premium/restricted and cannot be analyzed. Please select free articles for AI summarization.")
            
            if excluded_count > 0:
                print(f"📝 Excluded {excluded_count} premium articles from AI analysis")
            
            # Use filtered content IDs for summarization
            summary = summarizer_service.summarize_content(
                content_ids=filtered_ids,
                prompt=request.prompt
            )
            
            # Add metadata about filtering
            if hasattr(summary, 'summary_text'):
                if excluded_count > 0:
                    summary.summary_text = f"*Note: {excluded_count} premium/restricted articles were excluded from this analysis.*\n\n" + summary.summary_text
            
            return summary
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")

@app.post("/api/summarize/business-models")
async def analyze_business_models(content_ids: List[int]):
    """Specialized analysis for media business models."""
    try:
        summary = summarizer_service.analyze_business_models(content_ids)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Business model analysis failed: {str(e)}")

@app.post("/api/summarize/creator-economy")
async def analyze_creator_economy(content_ids: List[int]):
    """Specialized analysis for creator economy trends."""
    try:
        summary = summarizer_service.analyze_creator_economy(content_ids)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Creator economy analysis failed: {str(e)}")

@app.post("/api/summarize/vc-trends")
async def analyze_vc_trends(content_ids: List[int]):
    """Specialized analysis for VC investment trends."""
    try:
        summary = summarizer_service.analyze_vc_trends(content_ids)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"VC trends analysis failed: {str(e)}")

# User Management
@app.post("/api/users/{user_id}/sources/{source_id}")
async def add_user_source(user_id: int, source_id: int, db: Session = Depends(get_db)):
    """Add a source to a user's selected sources."""
    # Check if user and source exist
    user = db.query(User).filter(User.id == user_id).first()
    source = db.query(Source).filter(Source.id == source_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    # Check if already exists
    existing = db.query(UserSource).filter(
        UserSource.user_id == user_id,
        UserSource.source_id == source_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Source already added to user")
    
    user_source = UserSource(user_id=user_id, source_id=source_id)
    db.add(user_source)
    db.commit()
    
    return {"message": "Source added to user successfully"}

@app.delete("/api/users/{user_id}/sources/{source_id}")
async def remove_user_source(user_id: int, source_id: int, db: Session = Depends(get_db)):
    """Remove a source from a user's selected sources."""
    user_source = db.query(UserSource).filter(
        UserSource.user_id == user_id,
        UserSource.source_id == source_id
    ).first()
    
    if not user_source:
        raise HTTPException(status_code=404, detail="User source not found")
    
    db.delete(user_source)
    db.commit()
    
    return {"message": "Source removed from user successfully"}

@app.get("/api/users/{user_id}/content")
async def get_user_content(
    user_id: int,
    limit: int = Query(50, description="Number of items to return"),
    source_types: Optional[List[str]] = Query(None, description="Filter by source types"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags")
):
    """Get content for a specific user based on their selected sources."""
    try:
        contents = content_aggregator.get_user_content(
            user_id=user_id,
            limit=limit,
            source_types=source_types,
            tags=tags
        )
        return {"user_id": user_id, "content": contents, "count": len(contents)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user content: {str(e)}")

# Alerts
@app.post("/api/alerts")
async def create_alert(alert: AlertCreate, user_id: int, db: Session = Depends(get_db)):
    """Create a new alert for a user."""
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_alert = Alert(**alert.dict(), user_id=user_id)
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    
    return db_alert

@app.get("/api/alerts/{user_id}")
async def get_user_alerts(user_id: int, db: Session = Depends(get_db)):
    """Get all alerts for a user."""
    alerts = db.query(Alert).filter(Alert.user_id == user_id, Alert.is_active == True).all()
    return {"user_id": user_id, "alerts": alerts}

# Scheduled Tasks
@app.post("/api/scheduled-tasks")
async def create_scheduled_task(task: ScheduledTaskCreate, user_id: int, db: Session = Depends(get_db)):
    """Create a new scheduled task for a user."""
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_task = ScheduledTask(**task.dict(), user_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return db_task

@app.get("/api/scheduled-tasks/{user_id}")
async def get_user_scheduled_tasks(user_id: int, db: Session = Depends(get_db)):
    """Get all scheduled tasks for a user."""
    tasks = db.query(ScheduledTask).filter(ScheduledTask.user_id == user_id, ScheduledTask.is_active == True).all()
    return {"user_id": user_id, "tasks": tasks}

# Analytics
@app.get("/api/analytics/content-stats")
async def get_content_statistics(user_id: Optional[int] = Query(None, description="User ID for user-specific stats")):
    """Get content statistics and analytics."""
    try:
        stats = content_aggregator.get_content_statistics(user_id=user_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

# Admin endpoints
@app.post("/api/admin/cleanup")
async def cleanup_old_content(days_to_keep: int = Query(90, description="Number of days of content to keep")):
    """Clean up old content to manage database size."""
    try:
        deleted_count = content_aggregator.cleanup_old_content(days_to_keep)
        return {"message": f"Cleaned up {deleted_count} old content items", "deleted_count": deleted_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )

@app.post("/admin/populate-db")
async def populate_database_endpoint():
    """Admin endpoint to populate database with sample data."""
    try:
        # Import here to avoid issues
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from scripts.populate_render_db import populate_database
        result = populate_database()
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/populate-data")
async def populate_data():
    """Add sample data to empty database"""
    try:
        from src.database import SessionLocal
        from src.models import Source, Content
        from datetime import datetime
        
        db = SessionLocal()
        
        # Check if data already exists
        existing_content = db.query(Content).count()
        if existing_content > 0:
            return {"message": f"Database already has {existing_content} items"}
        
        # Add sources
        sources = [
            Source(name="TechCrunch", url="https://techcrunch.com", source_type="media", is_active=True),
            Source(name="Creator Report", url="https://creator.com", source_type="creator", is_active=True),
            Source(name="Business News", url="https://business.com", source_type="business_models", is_active=True),
            Source(name="Podcast Hub", url="https://podcast.com", source_type="podcasts", is_active=True)
        ]
        for source in sources:
            db.add(source)
        db.commit()
        
        # Add your actual content titles
        contents = [
            Content(title="Everything Mark Zuckerberg has gotten from Donald Trump so far", description="Meta CEO and political developments analysis", content_url="https://example.com/1", source_id=1, published_at=datetime.now()),
            Content(title="A ChatGPT tragedy is only the beginning", description="AI implications and societal impact", content_url="https://example.com/2", source_id=1, published_at=datetime.now()),
            Content(title="Musk sues over Grok flop", description="Legal challenges with AI chatbot", content_url="https://example.com/3", source_id=1, published_at=datetime.now()),
            Content(title="Creator Economy Hits $104 Billion", description="Record growth in creator platforms", content_url="https://example.com/4", source_id=2, published_at=datetime.now()),
            Content(title="Subscription Business Models in 2024", description="Analysis of subscription strategies", content_url="https://example.com/5", source_id=3, published_at=datetime.now()),
            Content(title="The Future of Podcast Monetization", description="New revenue streams for creators", content_url="https://example.com/6", source_id=4, published_at=datetime.now())
        ]
        for content in contents:
            db.add(content)
        db.commit()
        db.close()
        
        return {"success": True, "sources": 4, "content": 6}
    except Exception as e:
        return {"error": str(e)}



@app.get("/migrate-real-data")
async def migrate_real_data_endpoint():
    """Replace sample data with real 401 content items"""
    try:
        from scripts.migrate_real_data import migrate_real_data
        result = migrate_real_data()
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}



@app.get("/fixed-migrate")
async def fixed_migrate_endpoint():
    """Fixed migration with proper datetime handling"""
    try:
        from scripts.fixed_migration import fixed_migrate
        result = fixed_migrate()
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/migrate-all-content")
async def migrate_all_content_endpoint():
    """Load all 401 content items from real_content.json"""
    try:
        import json
        from datetime import datetime
        from src.database import SessionLocal
        from src.models import Content
        
        db = SessionLocal()
        
        # Clear existing content (keep sources)
        db.query(Content).delete()
        db.commit()
        
        # Load all content from real_content.json
        with open('real_content.json', 'r') as f:
            contents_data = json.load(f)
        
        successful_imports = 0
        failed_imports = 0
        
        for content_data in contents_data:  # Load ALL items, not just first 50
            try:
                # Clean and validate content data
                clean_content = {
                    'title': content_data.get('title', 'Untitled'),
                    'description': content_data.get('description'),
                    'content_url': content_data.get('content_url'),
                    'source_id': content_data.get('source_id', 1),
                    'author': content_data.get('author'),
                    'published_at': datetime.now(),  # Use current time for simplicity
                    'tags': content_data.get('tags') if content_data.get('tags') else []
                }
                
                # Skip items with no title or invalid source_id
                if not clean_content['title'] or clean_content['title'] == 'Page not found.':
                    failed_imports += 1
                    continue
                    
                content = Content(**clean_content)
                db.add(content)
                successful_imports += 1
                
            except Exception as e:
                print(f"Failed to import item: {e}")
                failed_imports += 1
                continue
        
        db.commit()
        db.close()
        
        return {
            "status": "success", 
            "data": {
                "total_items_processed": len(contents_data),
                "successful_imports": successful_imports,
                "failed_imports": failed_imports,
                "message": f"Successfully loaded {successful_imports} content items!"
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

