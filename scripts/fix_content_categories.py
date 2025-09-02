#!/usr/bin/env python3
"""
Fix content categories and tags for better filtering
"""

import sys
import os
from datetime import datetime, timezone

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import SessionLocal
from src.models import Content, Source

def categorize_content_by_keywords(title, description, source_name):
    """Categorize content based on keywords and source"""
    text = f"{title} {description} {source_name}".lower()
    
    categories = []
    
    # Creator Economy
    creator_keywords = [
        'creator', 'influencer', 'youtube', 'tiktok', 'instagram', 'social media',
        'monetization', 'brand deal', 'sponsorship', 'patreon', 'onlyfans',
        'content creation', 'subscriber', 'follower', 'viral', 'algorithm',
        'tubefilter', 'creator economy'
    ]
    if any(keyword in text for keyword in creator_keywords):
        categories.extend(['creator_economy', 'creator_monetization'])
    
    # Business/Startup
    business_keywords = [
        'startup', 'funding', 'investment', 'vc', 'venture capital', 'series a',
        'seed', 'ipo', 'acquisition', 'merger', 'business model', 'revenue',
        'growth', 'market', 'industry', 'entrepreneur'
    ]
    if any(keyword in text for keyword in business_keywords):
        categories.extend(['business_models', 'startup_funding'])
    
    # Media Analysis
    media_keywords = [
        'media business', 'streaming', 'netflix', 'disney', 'platform',
        'advertising', 'subscription', 'cord cutting', 'digital media',
        'content strategy', 'audience', 'engagement', 'media company',
        'journalism', 'publishing', 'news'
    ]
    if any(keyword in text for keyword in media_keywords):
        categories.extend(['media_analysis', 'media_business_models'])
    
    # Tech/AI
    tech_keywords = [
        'artificial intelligence', 'ai', 'machine learning', 'blockchain',
        'cryptocurrency', 'web3', 'metaverse', 'saas', 'platform', 'api',
        'technology', 'software', 'app', 'digital'
    ]
    if any(keyword in text for keyword in tech_keywords):
        categories.extend(['tech_news', 'ai_content_creation'])
    
    # VC Insights
    vc_keywords = [
        'venture capital', 'vc fund', 'investment firm', 'private equity',
        'portfolio', 'unicorn', 'valuation', 'exit strategy', 'due diligence'
    ]
    if any(keyword in text for keyword in vc_keywords):
        categories.append('vc_insights')
    
    # Source-based categorization
    if 'business insider' in source_name.lower():
        categories.extend(['business_news', 'business_models'])
    elif 'forbes' in source_name.lower():
        categories.extend(['business_news', 'business_models'])
    elif 'tubefilter' in source_name.lower():
        categories.extend(['creator_economy', 'creator_monetization'])
    elif 'yourstory' in source_name.lower():
        categories.extend(['indian_startups', 'startup_funding'])
    elif 'social media today' in source_name.lower():
        categories.extend(['creator_economy', 'media_analysis'])
    
    return list(set(categories))  # Remove duplicates

def fix_content_categories():
    """Fix categories for all existing content"""
    print("🔧 Fixing content categories and tags...")
    
    db = SessionLocal()
    try:
        # Get all content with their sources
        contents = db.query(Content).join(Source).all()
        
        updated_count = 0
        
        for content in contents:
            source = db.query(Source).filter(Source.id == content.source_id).first()
            
            if not source:
                continue
            
            # Categorize the content
            categories = categorize_content_by_keywords(
                content.title or '',
                content.description or '', 
                source.name
            )
            
            if categories:
                # Update tags
                existing_tags = content.tags or []
                new_tags = list(set(existing_tags + categories))
                content.tags = new_tags
                
                # Update engagement metrics
                if not content.engagement_metrics:
                    content.engagement_metrics = {}
                
                content.engagement_metrics.update({
                    'categories': categories,
                    'auto_categorized': True,
                    'categorized_at': datetime.now(timezone.utc).isoformat()
                })
                
                updated_count += 1
                
                print(f"✅ Updated: {content.title[:50]}... → {categories}")
        
        db.commit()
        print(f"\n🎉 Successfully categorized {updated_count} content items!")
        
        # Show category distribution
        category_counts = {}
        for content in contents:
            if content.tags:
                for tag in content.tags:
                    category_counts[tag] = category_counts.get(tag, 0) + 1
        
        print("\n📊 Category distribution:")
        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            if count > 1:  # Only show categories with multiple items
                print(f"  {category}: {count} items")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_content_categories()
