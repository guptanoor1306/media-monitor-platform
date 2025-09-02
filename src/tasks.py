#!/usr/bin/env python3
"""
Celery tasks for automated scraping and processing
"""

from celery import current_task
from datetime import datetime, timezone, timedelta
import asyncio
import logging

from .celery_app import celery_app
from .scraper_service import run_daily_scrape, MediaScraperService
from .database import SessionLocal
from .models import Content, Source, Summary

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def daily_scrape_media_sources(self):
    """Daily scraping of all media business sources"""
    try:
        logger.info("🚀 Starting daily media scrape task")
        
        # Update task status
        self.update_state(state='PROGRESS', meta={'status': 'Starting daily scrape'})
        
        # Run the async scraping function
        results = asyncio.run(run_daily_scrape())
        
        # Calculate summary
        total_added = sum(results.values())
        successful_sources = len([count for count in results.values() if count > 0])
        
        logger.info(f"✅ Daily scrape completed: {total_added} items from {successful_sources} sources")
        
        return {
            'status': 'completed',
            'total_items_added': total_added,
            'successful_sources': successful_sources,
            'results': results,
            'completed_at': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Daily scrape failed: {str(e)}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

@celery_app.task(bind=True)
def hourly_priority_scrape(self):
    """Hourly scraping of high-priority sources"""
    try:
        logger.info("⚡ Starting hourly priority scrape")
        
        # Define high-priority sources that update frequently
        priority_sources = [
            'All-In Podcast',
            'a16z Blog', 
            'Stratechery',
            'Creator Economy Report',
            'Colin and Samir'
        ]
        
        self.update_state(state='PROGRESS', meta={'status': 'Scraping priority sources'})
        
        # Run focused scrape on priority sources
        async def priority_scrape():
            async with MediaScraperService() as scraper:
                results = {}
                for source_name in priority_sources:
                    if source_name in scraper.PREMIUM_MEDIA_SOURCES:
                        source_data = scraper.PREMIUM_MEDIA_SOURCES[source_name]
                        count = await scraper.scrape_rss_feed(source_name, source_data)
                        results[source_name] = count
                return results
        
        results = asyncio.run(priority_scrape())
        total_added = sum(results.values())
        
        logger.info(f"⚡ Hourly scrape completed: {total_added} items")
        
        return {
            'status': 'completed',
            'total_items_added': total_added,
            'results': results,
            'completed_at': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Hourly scrape failed: {str(e)}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

@celery_app.task(bind=True)
def weekly_comprehensive_scrape(self):
    """Weekly comprehensive scraping including older content"""
    try:
        logger.info("📅 Starting weekly comprehensive scrape")
        
        self.update_state(state='PROGRESS', meta={'status': 'Running comprehensive scrape'})
        
        # This would include more sources and longer time ranges
        results = asyncio.run(run_daily_scrape())
        
        # Also clean up and organize content
        db = SessionLocal()
        try:
            # Count total content
            total_content = db.query(Content).count()
            
            # Clean up very old content (>6 months)
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=180)
            old_content = db.query(Content).filter(Content.created_at < cutoff_date)
            deleted_count = old_content.count()
            old_content.delete()
            
            db.commit()
            
            logger.info(f"📅 Weekly scrape completed: {sum(results.values())} new items, {deleted_count} old items cleaned")
            
            return {
                'status': 'completed',
                'total_items_added': sum(results.values()),
                'total_content': total_content,
                'old_items_cleaned': deleted_count,
                'results': results,
                'completed_at': datetime.now(timezone.utc).isoformat()
            }
            
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"❌ Weekly scrape failed: {str(e)}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

@celery_app.task(bind=True)
def cleanup_old_content(self):
    """Monthly cleanup of old content and summaries"""
    try:
        logger.info("🧹 Starting monthly cleanup")
        
        db = SessionLocal()
        try:
            # Delete content older than 1 year
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=365)
            
            # Delete old summaries first (foreign key constraint)
            old_summaries = db.query(Summary).join(Content).filter(Content.created_at < cutoff_date)
            summaries_deleted = old_summaries.count()
            old_summaries.delete(synchronize_session=False)
            
            # Delete old content
            old_content = db.query(Content).filter(Content.created_at < cutoff_date)
            content_deleted = old_content.count()
            old_content.delete()
            
            db.commit()
            
            logger.info(f"🧹 Cleanup completed: {content_deleted} content items, {summaries_deleted} summaries deleted")
            
            return {
                'status': 'completed',
                'content_deleted': content_deleted,
                'summaries_deleted': summaries_deleted,
                'completed_at': datetime.now(timezone.utc).isoformat()
            }
            
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {str(e)}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

@celery_app.task(bind=True)
def manual_scrape_source(self, source_name: str):
    """Manually trigger scraping for a specific source"""
    try:
        logger.info(f"🎯 Manual scrape requested for: {source_name}")
        
        async def single_source_scrape():
            async with MediaScraperService() as scraper:
                if source_name in scraper.PREMIUM_MEDIA_SOURCES:
                    source_data = scraper.PREMIUM_MEDIA_SOURCES[source_name]
                    return await scraper.scrape_rss_feed(source_name, source_data)
                return 0
        
        count = asyncio.run(single_source_scrape())
        
        return {
            'status': 'completed',
            'source': source_name,
            'items_added': count,
            'completed_at': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Manual scrape failed for {source_name}: {str(e)}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise
