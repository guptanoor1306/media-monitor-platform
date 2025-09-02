# This script creates sample data directly in the PostgreSQL database
from src.database import SessionLocal
from src.models import Source, Content
from datetime import datetime

def populate_database():
    db = SessionLocal()
    try:
        # Clear existing data
        db.query(Content).delete()
        db.query(Source).delete()
        db.commit()
        
        # Add sources for each bucket
        sources_data = [
            # Media Industry
            {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "source_type": "media"},
            {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "source_type": "media"},
            {"name": "Wired", "url": "https://www.wired.com/feed/", "source_type": "media"},
            
            # Creator Economy
            {"name": "Creator Economy Report", "url": "https://creatoreconomy.so/feed", "source_type": "creator"},
            {"name": "ConvertKit Creator", "url": "https://convertkit.com/blog/feed", "source_type": "creator"},
            {"name": "Beehiiv Blog", "url": "https://blog.beehiiv.com/feed", "source_type": "creator"},
            
            # Business Models
            {"name": "Harvard Business Review", "url": "https://feeds.hbr.org/harvardbusiness", "source_type": "business_models"},
            {"name": "Fast Company", "url": "https://www.fastcompany.com/rss.xml", "source_type": "business_models"},
            {"name": "Business Insider", "url": "https://feeds.businessinsider.com/custom/all", "source_type": "business_models"},
            
            # Podcasts
            {"name": "All-In Podcast", "url": "https://feeds.megaphone.fm/all-in", "source_type": "podcasts"},
            {"name": "Tim Ferriss Show", "url": "https://rss.art19.com/tim-ferriss-show", "source_type": "podcasts"},
            {"name": "Masters of Scale", "url": "https://feeds.megaphone.fm/WWO9155077384", "source_type": "podcasts"},
        ]
        
        # Create sources
        source_objects = []
        for i, source_data in enumerate(sources_data, 1):
            source = Source(
                id=i,
                name=source_data["name"],
                url=source_data["url"],
                source_type=source_data["source_type"],
                is_active=True,
                created_at=datetime.now()
            )
            db.add(source)
            source_objects.append(source)
        
        db.commit()
        
        # Add sample content
        sample_content = [
            {
                "title": "Everything Mark Zuckerberg has gotten from Donald Trump so far",
                "description": "Analysis of the relationship between Meta's CEO and the former president, including policy changes and business implications.",
                "source_id": 1,
                "tags": ["meta", "politics", "social media"]
            },
            {
                "title": "A ChatGPT tragedy is only the beginning",
                "description": "Exploring the darker implications of AI advancement and its impact on society.",
                "source_id": 1,
                "tags": ["ai", "chatgpt", "technology"]
            },
            {
                "title": "Musk sues over Grok flop",
                "description": "Elon Musk's legal challenges following issues with his AI chatbot Grok.",
                "source_id": 1,
                "tags": ["elon musk", "ai", "legal"]
            },
            {
                "title": "Creator Economy Reaches $104 Billion Milestone",
                "description": "New data shows unprecedented growth in creator monetization across all platforms and industries.",
                "source_id": 4,
                "tags": ["creator economy", "monetization", "growth"]
            },
            {
                "title": "The Rise of Newsletter Business Models",
                "description": "How independent creators are building sustainable businesses through newsletter subscriptions.",
                "source_id": 4,
                "tags": ["newsletter", "subscription", "business model"]
            },
            {
                "title": "Subscription Fatigue: What Businesses Need to Know",
                "description": "Analysis of changing consumer behavior toward subscription services and implications for businesses.",
                "source_id": 7,
                "tags": ["subscription", "consumer behavior", "business strategy"]
            },
            {
                "title": "The Future of Podcast Monetization in 2024",
                "description": "Exploring new revenue streams and business models for podcast creators beyond traditional advertising.",
                "source_id": 10,
                "tags": ["podcast", "monetization", "audio content"]
            },
            {
                "title": "How AI is Transforming Content Creation",
                "description": "Deep dive into artificial intelligence tools and their impact on creative industries.",
                "source_id": 2,
                "tags": ["ai", "content creation", "creative industry"]
            }
        ]
        
        # Create content
        for i, content_data in enumerate(sample_content, 1):
            content = Content(
                id=i,
                title=content_data["title"],
                description=content_data["description"],
                content_url=f"https://example.com/article-{i}",
                source_id=content_data["source_id"],
                author="Editorial Team",
                published_at=datetime.now(),
                tags=content_data["tags"],
                created_at=datetime.now()
            )
            db.add(content)
        
        db.commit()
        
        print(f"✅ Database populated successfully!")
        print(f"📊 Added {len(sources_data)} sources and {len(sample_content)} content items")
        return {"sources": len(sources_data), "content": len(sample_content)}
        
    except Exception as e:
        print(f"❌ Error populating database: {e}")
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

if __name__ == "__main__":
    populate_database()
