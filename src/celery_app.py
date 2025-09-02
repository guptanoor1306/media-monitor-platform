#!/usr/bin/env python3
"""
Celery configuration for automated scraping tasks
"""

from celery import Celery
from celery.schedules import crontab
from datetime import datetime
import os

from .config import settings

# Create Celery app
celery_app = Celery(
    'media_monitor',
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=['src.tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Scheduled tasks
celery_app.conf.beat_schedule = {
    # Daily scraping at 6 AM UTC (early morning)
    'daily-media-scrape': {
        'task': 'src.tasks.daily_scrape_media_sources',
        'schedule': crontab(hour=6, minute=0),  # 6:00 AM UTC daily
    },
    
    # Hourly scraping for high-priority sources
    'hourly-priority-scrape': {
        'task': 'src.tasks.hourly_priority_scrape',
        'schedule': crontab(minute=0),  # Every hour
    },
    
    # Weekly comprehensive scrape (Sundays at 2 AM)
    'weekly-comprehensive-scrape': {
        'task': 'src.tasks.weekly_comprehensive_scrape', 
        'schedule': crontab(hour=2, minute=0, day_of_week=0),  # Sunday 2 AM
    },
    
    # Cleanup old content (monthly)
    'monthly-cleanup': {
        'task': 'src.tasks.cleanup_old_content',
        'schedule': crontab(hour=3, minute=0, day_of_month=1),  # 1st of month 3 AM
    }
}

if __name__ == '__main__':
    celery_app.start()
