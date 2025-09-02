from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.models import Source, Content, UserSource
from src.scrapers.blog_scraper import BlogScraper
###from src.scrapers.social_scraper import TwitterScraper, RedditScraper
from src.scrapers.podcast_scraper import PodcastScraper
from src.config import settings


class ContentAggregator:
    """Service for aggregating content from various sources."""
    
    def __init__(self):
        self.scrapers = {
            'blog': BlogScraper(),
            'twitter': TwitterScraper(),
            'reddit': RedditScraper(),
            'podcast': PodcastScraper()
        }
    
    def update_all_sources(self) -> Dict[str, int]:
        """Update content from all active sources."""
        db = SessionLocal()
        try:
            sources = db.query(Source).filter(Source.is_active == True).all()
            results = {}
            
            for source in sources:
                try:
                    count = self._update_source_content(source, db)
                    results[source.name] = count
                    
                    # Update source last_updated timestamp
                    source.last_updated = datetime.utcnow()
                    db.commit()
                    
                except Exception as e:
                    print(f"Error updating source {source.name}: {e}")
                    results[source.name] = 0
            
            return results
            
        finally:
            db.close()
    
    def update_user_sources(self, user_id: int) -> Dict[str, int]:
        """Update content from sources selected by a specific user."""
        db = SessionLocal()
        try:
            user_sources = db.query(UserSource).filter(
                UserSource.user_id == user_id,
                UserSource.is_active == True
            ).all()
            
            results = {}
            for user_source in user_sources:
                source = user_source.source
                try:
                    count = self._update_source_content(source, db)
                    results[source.name] = count
                    
                    # Update source last_updated timestamp
                    source.last_updated = datetime.utcnow()
                    db.commit()
                    
                except Exception as e:
                    print(f"Error updating user source {source.name}: {e}")
                    results[source.name] = 0
            
            return results
            
        finally:
            db.close()
    
    def _update_source_content(self, source: Source, db: Session) -> int:
        """Update content from a specific source."""
        scraper = self._get_scraper_for_source(source)
        if not scraper:
            print(f"No scraper available for source type: {source.source_type}")
            return 0
        
        try:
            # Scrape new content
            new_contents = scraper.scrape_content(source.url)
            
            # Filter out content that already exists
            existing_urls = set()
            existing_contents = db.query(Content).filter(Content.source_id == source.id).all()
            for content in existing_contents:
                if content.content_url:
                    existing_urls.add(content.content_url)
            
            # Add new content to database
            added_count = 0
            for content in new_contents:
                if content.content_url and content.content_url not in existing_urls:
                    content.source_id = source.id
                    db.add(content)
                    added_count += 1
            
            db.commit()
            print(f"Added {added_count} new content items from {source.name}")
            return added_count
            
        except Exception as e:
            print(f"Error scraping source {source.name}: {e}")
            db.rollback()
            return 0
    
    def _get_scraper_for_source(self, source: Source):
        """Get the appropriate scraper for a source type."""
        source_type = source.source_type.lower()
        
        if 'blog' in source_type or 'news' in source_type or 'substack' in source_type:
            return self.scrapers['blog']
        elif 'twitter' in source_type:
            return self.scrapers['twitter']
        elif 'reddit' in source_type:
            return self.scrapers['reddit']
        elif 'podcast' in source_type or 'spotify' in source_type:
            return self.scrapers['podcast']
        else:
            # Try to auto-detect based on URL
            return self._auto_detect_scraper(source.url)
    
    def _auto_detect_scraper(self, url: str):
        """Auto-detect the appropriate scraper based on URL."""
        url_lower = url.lower()
        
        if 'twitter.com' in url_lower or 'x.com' in url_lower:
            return self.scrapers['twitter']
        elif 'reddit.com' in url_lower:
            return self.scrapers['reddit']
        elif 'spotify.com' in url_lower:
            return self.scrapers['podcast']
        elif 'substack.com' in url_lower:
            return self.scrapers['blog']
        else:
            # Default to blog scraper for unknown URLs
            return self.scrapers['blog']
    
    def get_user_content(self, user_id: int, limit: int = 50, 
                        source_types: Optional[List[str]] = None,
                        tags: Optional[List[str]] = None,
                        date_from: Optional[datetime] = None) -> List[Content]:
        """Get content for a specific user based on their selected sources and filters."""
        db = SessionLocal()
        try:
            # Get user's active sources
            query = db.query(Content).join(UserSource).filter(
                UserSource.user_id == user_id,
                UserSource.is_active == True
            )
            
            # Apply source type filter
            if source_types:
                query = query.join(Source).filter(Source.source_type.in_(source_types))
            
            # Apply tag filter
            if tags:
                # This is a simplified tag search - in production you might want more sophisticated text search
                tag_conditions = []
                for tag in tags:
                    tag_conditions.append(Content.tags.contains([tag]))
                query = query.filter(or_(*tag_conditions))
            
            # Apply date filter
            if date_from:
                query = query.filter(Content.published_at >= date_from)
            
            # Order by published date (newest first)
            query = query.order_by(Content.published_at.desc())
            
            # Apply limit
            contents = query.limit(limit).all()
            
            return contents
            
        finally:
            db.close()
    
    def search_content(self, query: str, user_id: Optional[int] = None, 
                      limit: int = 50) -> List[Content]:
        """Search content across all sources using simple keyword matching."""
        db = SessionLocal()
        try:
            if user_id:
                # Search only in user's selected sources
                base_query = db.query(Content).join(UserSource).filter(
                    UserSource.user_id == user_id,
                    UserSource.is_active == True
                )
            else:
                # Search across all sources
                base_query = db.query(Content)
            
            # Clean and prepare search query
            search_terms = query.strip().lower().split()
            if not search_terms:
                return []
            
            # Build search conditions for each term
            search_conditions = []
            for term in search_terms:
                term_pattern = f"%{term}%"
                term_conditions = or_(
                    Content.title.ilike(term_pattern),
                    Content.description.ilike(term_pattern),
                    Content.content_text.ilike(term_pattern),
                    Content.author.ilike(term_pattern)
                )
                search_conditions.append(term_conditions)
            
            # Combine all conditions with AND logic (all terms must match)
            if len(search_conditions) == 1:
                final_condition = search_conditions[0]
            else:
                final_condition = and_(*search_conditions)
            
            contents = base_query.filter(final_condition)\
                                .order_by(Content.published_at.desc())\
                                .limit(limit).all()
            
            print(f"🔍 Search for '{query}' found {len(contents)} results")
            return contents
            
        except Exception as e:
            print(f"Search error: {e}")
            return []
        finally:
            db.close()
    
    def get_content_statistics(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get content statistics for analytics."""
        db = SessionLocal()
        try:
            if user_id:
                # Statistics for user's sources only
                base_query = db.query(Content).join(UserSource).filter(
                    UserSource.user_id == user_id,
                    UserSource.is_active == True
                )
            else:
                # Statistics for all sources
                base_query = db.query(Content)
            
            # Total content count
            total_count = base_query.count()
            
            # Content by source type
            source_type_stats = db.query(
                Source.source_type,
                func.count(Content.id)
            ).join(Content).group_by(Source.source_type).all()
            
            # Content by date (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_count = base_query.filter(Content.published_at >= thirty_days_ago).count()
            
            # Top tags
            tag_stats = {}
            contents = base_query.all()
            for content in contents:
                if content.tags:
                    for tag in content.tags:
                        tag_stats[tag] = tag_stats.get(tag, 0) + 1
            
            # Sort tags by frequency
            top_tags = sorted(tag_stats.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                'total_content': total_count,
                'recent_content': recent_count,
                'by_source_type': dict(source_type_stats),
                'top_tags': top_tags
            }
            
        finally:
            db.close()
    
    def cleanup_old_content(self, days_to_keep: int = 90) -> int:
        """Remove old content to manage database size."""
        db = SessionLocal()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            # Count old content
            old_content_count = db.query(Content).filter(
                Content.published_at < cutoff_date
            ).count()
            
            # Delete old content
            db.query(Content).filter(
                Content.published_at < cutoff_date
            ).delete()
            
            db.commit()
            print(f"Cleaned up {old_content_count} old content items")
            return old_content_count
            
        except Exception as e:
            print(f"Error cleaning up old content: {e}")
            db.rollback()
            return 0
        finally:
            db.close()


# Import missing dependencies
from sqlalchemy import or_, and_, func
