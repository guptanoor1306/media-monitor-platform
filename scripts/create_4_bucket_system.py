#!/usr/bin/env python3
"""
Create 4-bucket magazine system focused on Media & Creator Economy
"""

import asyncio
import aiohttp
import feedparser
import sys
import os
import ssl
from datetime import datetime, timezone, timedelta
from urllib.parse import urljoin
import re

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import SessionLocal, init_db
from src.models import Source, Content, Summary

# 4 FOCUSED BUCKETS for Media & Creator Economy Magazine
MAGAZINE_SOURCES = {
    
    # BUCKET 1: MEDIA INDUSTRY NEWS
    'media': {
        'Platformer (Casey Newton)': 'https://www.platformer.news/feed',
        'The Information': 'https://www.theinformation.com/feed', 
        'Nieman Lab': 'http://www.niemanlab.org/feed/',
        'Poynter': 'https://www.poynter.org/feed/',
        'Columbia Journalism Review': 'https://www.cjr.org/feed.rss',
        'Digiday': 'https://digiday.com/feed/',
        'AdAge': 'https://adage.com/rss.xml',
        'Marketing Land': 'https://marketingland.com/feed',
        'TechMeme': 'https://www.techmeme.com/feed.xml',
        'Axios Media': 'https://www.axios.com/media/feed/',
        'The Wrap': 'https://www.thewrap.com/feed/',
        'Variety': 'https://variety.com/feed/',
        'Hollywood Reporter': 'https://www.hollywoodreporter.com/feed/',
        'Media Post': 'https://www.mediapost.com/rss/',
        'Press Gazette': 'https://pressgazette.co.uk/feed/',
    },
    
    # BUCKET 2: CREATOR ECONOMY (Indian + Global)
    'creator': {
        # Global Creator Economy
        'Creator Economy Report': 'https://creatoreconomy.so/feed/',
        'ConvertKit Creator Economy': 'https://convertkit.com/creator-economy/feed',
        'The Tilt': 'https://www.thetilt.com/rss',
        'Not Boring by Packy McCormick': 'https://www.notboring.co/feed',
        'Morning Brew Creator Economy': 'https://www.morningbrew.com/creator-economy/feed',
        
        # YouTube Creator News
        'YouTube Creator Blog': 'https://youtube-creators.googleblog.com/feeds/posts/default',
        'TubeBuddy Blog': 'https://www.tubebuddy.com/blog/feed',
        'VidIQ Blog': 'https://vidiq.com/blog/feed/',
        'Think Media': 'https://www.thinkmedia.com/feed/',
        
        # Indian Creator Sources
        'The Ken Creator': 'https://the-ken.com/category/creator-economy/feed/',
        'Inc42 Creator Economy': 'https://inc42.com/buzz/creator-economy/feed/',
        'YourStory Creator': 'https://yourstory.com/category/creator-economy/feed',
        'Economic Times Creator': 'https://economictimes.indiatimes.com/topic/creator-economy/rss',
        
        # Reddit Creator Communities
        'Reddit Creator Economy': 'http://www.reddit.com/r/creatoreconomy/.rss',
        'Reddit YouTube Creators': 'http://www.reddit.com/r/PartneredYoutube/.rss',
        'Reddit Content Creation': 'http://www.reddit.com/r/ContentCreation/.rss',
        'Reddit Creator Support': 'http://www.reddit.com/r/CreatorsAdvice/.rss',
    },
    
    # BUCKET 3: BUSINESS MODELS & MONETIZATION  
    'business_models': {
        # Media Business Models
        'Stratechery': 'https://stratechery.com/feed/',
        'The Rebooting': 'https://www.therebooting.com/feed/',
        'Whats New in Publishing': 'https://whatsnewinpublishing.com/feed/',
        'Nieman Lab Business': 'http://www.niemanlab.org/feed/',
        'Media Voices': 'https://www.mediavoices.org/feed/',
        'Pugpig': 'https://pugpig.com/feed/',
        'WAN-IFRA': 'https://wan-ifra.org/feed/',
        
        # VC/Investment in Media
        'a16z Media': 'https://a16z.com/tag/media/feed/',
        'First Round Review': 'https://review.firstround.com/feed',
        'Bessemer VP Media': 'https://www.bvp.com/atlas/media-investing',
        'Lightspeed Venture': 'https://lsvp.com/feed/',
        'Sequoia Capital': 'https://medium.com/feed/sequoia-capital',
        
        # Business Model Analysis
        'Harvard Business Review Media': 'http://feeds.hbr.org/harvardbusiness',
        'McKinsey Media': 'https://www.mckinsey.com/industries/technology-media-and-telecommunications/our-insights/rss',
        'PwC Media Outlook': 'https://www.pwc.com/gx/en/entertainment-media/outlook/feed.xml',
        'Deloitte Media': 'https://www2.deloitte.com/us/en/industries/technology-media-telecommunications/feed.xml',
    },
    
    # BUCKET 4: PODCASTS & AUDIO CONTENT
    'podcasts': {
        # Business/Creator Podcasts
        'All In Podcast': 'https://feeds.simplecast.com/JCLotU5d',
        'The Tim Ferriss Show': 'http://feeds.feedburner.com/thetimferrissshow',
        'How I Built This': 'https://feeds.npr.org/510313/podcast.xml',
        'Masters of Scale': 'https://feeds.megaphone.fm/mastersofscale',
        'The GaryVee Audio Experience': 'http://feeds.feedburner.com/garyvaynerchuk',
        'Smart Passive Income': 'http://feeds.feedburner.com/smartpassiveincome',
        'Entrepreneur on Fire': 'http://feeds.feedburner.com/eofire',
        'The Creator Economy Show': 'https://feeds.buzzsprout.com/1404486.rss',
        
        # Media/Tech Podcasts  
        'Recode Decode': 'https://feeds.megaphone.fm/recode-decode',
        'The Vergecast': 'https://feeds.megaphone.fm/vergecast',
        'Pivot': 'https://feeds.megaphone.fm/pivot',
        'Land of the Giants': 'https://feeds.megaphone.fm/land-of-the-giants',
        'Reply All': 'https://feeds.gimletmedia.com/reply-all',
        'StartUp Podcast': 'https://feeds.gimletmedia.com/hearstartup',
        
        # Indian Podcasts
        'The Seen and the Unseen': 'https://feeds.transistor.fm/the-seen-and-the-unseen',
        'IVM Podcast': 'https://ivmpodcasts.com/feed/podcast/',
        'The Desi VC': 'https://feeds.soundcloud.com/users/soundcloud:users:394895517/sounds.rss',
    }
}

async def fetch_magazine_content(session, name, url, bucket, days_back=90):
    """Fetch content for magazine-style display"""
    try:
        print(f"📡 Fetching {bucket.upper()}: {name}")
        
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=30)) as session:
            async with session.get(url, timeout=30) as response:
                if response.status != 200:
                    print(f"❌ HTTP {response.status} for {name}")
                    return []
                
                content = await response.text()
        
        # Parse RSS feed
        feed = feedparser.parse(content)
        
        if not hasattr(feed, 'entries') or not feed.entries:
            print(f"⚠️  No entries found in {name}")
            return []
        
        # Get recent content (3 months for magazine freshness)
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        recent_entries = []
        
        for entry in feed.entries:
            # Parse entry date
            entry_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                try:
                    entry_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                except:
                    pass
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                try:
                    entry_date = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
                except:
                    pass
            
            # Include recent entries or entries without dates
            if entry_date and entry_date >= cutoff_date:
                recent_entries.append((entry, bucket))
            elif not entry_date:  # Include entries without dates
                recent_entries.append((entry, bucket))
        
        print(f"✅ {name}: {len(recent_entries)} recent items")
        return recent_entries
        
    except Exception as e:
        print(f"❌ Error fetching {name}: {str(e)}")
        return []

async def create_magazine_sources():
    """Create 4-bucket magazine sources"""
    db = SessionLocal()
    
    try:
        print("🧹 Clearing old content for magazine system...")
        # Clear everything for fresh magazine start
        db.query(Summary).delete()
        db.query(Content).delete()
        db.query(Source).delete()
        db.commit()
        print("✅ Database cleared for magazine system")
        
        print("\n📂 Creating 4-BUCKET MAGAZINE SYSTEM...")
        total_sources_added = 0
        
        for bucket, sources in MAGAZINE_SOURCES.items():
            print(f"\n📁 BUCKET {bucket.upper()} ({len(sources)} sources):")
            
            for name, url in sources.items():
                source = Source(
                    name=name,
                    url=url,
                    source_type=bucket,  # Use bucket as source type
                    description=f"Magazine source: {name} ({bucket})",
                    is_active=True,
                    update_interval=3600
                )
                db.add(source)
                print(f"  ✅ {name}")
                total_sources_added += 1
        
        db.commit()
        print(f"\n🎉 Added {total_sources_added} magazine sources across 4 buckets!")
        return total_sources_added
        
    except Exception as e:
        print(f"❌ Error creating magazine sources: {e}")
        db.rollback()
        return 0
    finally:
        db.close()

async def populate_magazine_content():
    """Populate with magazine-style content"""
    db = SessionLocal()
    
    try:
        print("\n📰 POPULATING MAGAZINE CONTENT...")
        
        # Get all sources
        sources = db.query(Source).all()
        
        total_content = 0
        successful_sources = 0
        
        for source in sources:
            bucket = source.source_type
            
            try:
                connector = aiohttp.TCPConnector(ssl=False)
                async with aiohttp.ClientSession(connector=connector) as session:
                    # Fetch content for this source
                    entries_with_bucket = await fetch_magazine_content(session, source.name, source.url, bucket)
                
                if not entries_with_bucket:
                    continue
                
                # Process entries
                added_count = 0
                for entry, bucket_type in entries_with_bucket:
                    try:
                        # Extract content details
                        title = getattr(entry, 'title', 'No Title')
                        link = getattr(entry, 'link', '')
                        description = getattr(entry, 'summary', getattr(entry, 'description', ''))
                        
                        # Clean HTML from description
                        if description:
                            import re
                            description = re.sub(r'<[^>]+>', '', description)
                            description = description.strip()
                        
                        # Parse published date
                        published_at = None
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            try:
                                published_at = datetime(*entry.published_parsed[:6])
                            except:
                                published_at = datetime.now() - timedelta(days=7)
                        else:
                            published_at = datetime.now() - timedelta(days=7)
                        
                        # Extract author
                        author = getattr(entry, 'author', None)
                        
                        # Generate bucket-specific tags
                        tags = [bucket_type]  # Primary bucket tag
                        content_text = (title + " " + description).lower()
                        
                        # Bucket-specific tagging
                        if bucket_type == 'media':
                            tags.extend(['media_industry', 'journalism', 'publishing'])
                            if any(word in content_text for word in ['streaming', 'netflix', 'spotify', 'platform']):
                                tags.append('streaming_platforms')
                            if any(word in content_text for word in ['subscription', 'paywall', 'monetization']):
                                tags.append('media_monetization')
                                
                        elif bucket_type == 'creator':
                            tags.extend(['creator_economy', 'influencer', 'content_creator'])
                            if any(word in content_text for word in ['youtube', 'tiktok', 'instagram', 'social media']):
                                tags.append('social_platforms')
                            if any(word in content_text for word in ['sponsorship', 'brand', 'affiliate', 'monetization']):
                                tags.append('creator_monetization')
                            if any(word in content_text for word in ['indian', 'india', 'bollywood']):
                                tags.append('indian_creators')
                                
                        elif bucket_type == 'business_models':
                            tags.extend(['business_models', 'monetization', 'revenue'])
                            if any(word in content_text for word in ['saas', 'subscription', 'recurring']):
                                tags.append('subscription_models')
                            if any(word in content_text for word in ['advertising', 'ads', 'sponsored']):
                                tags.append('advertising_models')
                            if any(word in content_text for word in ['venture', 'funding', 'investment']):
                                tags.append('vc_funding')
                                
                        elif bucket_type == 'podcasts':
                            tags.extend(['podcast_content', 'audio', 'interview'])
                            if any(word in content_text for word in ['business', 'entrepreneur', 'startup']):
                                tags.append('business_podcasts')
                            if any(word in content_text for word in ['creator', 'content', 'media']):
                                tags.append('creator_podcasts')
                        
                        # Skip duplicates
                        existing = db.query(Content).filter(
                            Content.source_id == source.id,
                            Content.content_url == link
                        ).first()
                        
                        if existing:
                            continue
                        
                        # Create Content object
                        content = Content(
                            title=title[:500] if title else 'No Title',
                            description=description[:1000] if description else '',
                            content_url=link,
                            content_text=description[:2000] if description else '',
                            author=author[:100] if author else None,
                            published_at=published_at,
                            tags=tags,
                            source_id=source.id
                        )
                        
                        db.add(content)
                        added_count += 1
                        
                    except Exception as e:
                        print(f"⚠️  Error processing entry: {e}")
                        continue
                
                if added_count > 0:
                    db.commit()
                    total_content += added_count
                    successful_sources += 1
                    print(f"  ✅ Added {added_count} magazine items")
                    
            except Exception as e:
                print(f"  ❌ Error processing {source.name}: {e}")
                continue
        
        print(f"\n🎉 MAGAZINE POPULATION COMPLETE!")
        print(f"📊 Total magazine content: {total_content}")
        print(f"📂 Successful sources: {successful_sources}")
        
        # Show bucket breakdown
        for bucket in ['media', 'creator', 'business_models', 'podcasts']:
            count = db.query(Content).join(Source).filter(Source.source_type == bucket).count()
            bucket_display = {
                'media': '📺 MEDIA INDUSTRY',
                'creator': '🎭 CREATOR ECONOMY', 
                'business_models': '💼 BUSINESS MODELS',
                'podcasts': '🎧 PODCASTS'
            }
            print(f"{bucket_display[bucket]}: {count} items")
            
        return total_content
        
    except Exception as e:
        print(f"❌ Error during magazine population: {e}")
        db.rollback()
        return 0
    finally:
        db.close()

async def main():
    """Create 4-bucket magazine system"""
    print("🎯 CREATING 4-BUCKET MAGAZINE SYSTEM")
    print("📋 BUCKETS: Media Industry | Creator Economy | Business Models | Podcasts")
    print("=" * 80)
    
    # Initialize database
    init_db()
    
    # Step 1: Create magazine sources
    sources_added = await create_magazine_sources()
    
    if sources_added > 0:
        # Step 2: Populate magazine content
        content_added = await populate_magazine_content()
        
        print("\n" + "=" * 80)
        print("🎉 4-BUCKET MAGAZINE SYSTEM COMPLETE!")
        print(f"📂 Magazine sources: {sources_added}")
        print(f"📰 Magazine content: {content_added}")
        print("\n🎯 FOCUS AREAS:")
        print("  📺 Media Industry News")
        print("  🎭 Creator Economy (Indian + Global)")  
        print("  💼 Business Models & Monetization")
        print("  🎧 Podcasts & Audio Content")
        print("\n🌐 Ready for magazine dashboard: http://localhost:8001")
    else:
        print("❌ Failed to create magazine sources.")

if __name__ == "__main__":
    asyncio.run(main())
