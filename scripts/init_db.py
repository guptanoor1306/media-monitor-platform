#!/usr/bin/env python3
"""
Database initialization script with sample data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import SessionLocal, init_db
from src.models import Source, User, Base
from src.config import settings


def create_sample_data():
    """Create sample sources and users for testing."""
    db = SessionLocal()
    
    try:
        # Create comprehensive sample sources
        sample_sources = [
            # BLOGS & NEWS
            {
                "name": "Substack - Creator Economy",
                "url": "https://substack.com/topics/creator-economy",
                "source_type": "blog",
                "description": "Newsletters and blogs focused on creator economy trends",
                "update_interval": 3600
            },
            {
                "name": "a16z Blog",
                "url": "https://a16z.com/blog/",
                "source_type": "blog",
                "description": "Andreessen Horowitz's insights on technology and business",
                "update_interval": 7200
            },
            {
                "name": "Future Fund Blog",
                "url": "https://future.a16z.com/",
                "source_type": "blog",
                "description": "Future Fund's analysis of emerging technologies and trends",
                "update_interval": 7200
            },
            {
                "name": "Economic Times Prime",
                "url": "https://economictimes.indiatimes.com/prime",
                "source_type": "blog",
                "description": "Premium business and economic analysis",
                "update_interval": 3600
            },
            {
                "name": "TechCrunch",
                "url": "https://techcrunch.com/",
                "source_type": "blog",
                "description": "Latest technology news and startup information",
                "update_interval": 1800
            },
            {
                "name": "The Information",
                "url": "https://www.theinformation.com/",
                "source_type": "blog",
                "description": "In-depth tech journalism and analysis",
                "update_interval": 3600
            },
            {
                "name": "Stratechery",
                "url": "https://stratechery.com/",
                "source_type": "blog",
                "description": "Ben Thompson's analysis of tech strategy and business",
                "update_interval": 86400
            },
            {
                "name": "Not Boring",
                "url": "https://www.notboring.co/",
                "source_type": "blog",
                "description": "Packy McCormick's newsletter on business and technology",
                "update_interval": 86400
            },
            {
                "name": "The Generalist",
                "url": "https://www.readthegeneralist.com/",
                "source_type": "blog",
                "description": "Mario Gabriele's analysis of business and technology",
                "update_interval": 86400
            },
            {
                "name": "Platformer",
                "url": "https://www.platformer.news/",
                "source_type": "blog",
                "description": "Casey Newton's newsletter on social media and tech platforms",
                "update_interval": 86400
            },
            {
                "name": "Axios",
                "url": "https://www.axios.com/",
                "source_type": "blog",
                "description": "Breaking news and analysis on business and technology",
                "update_interval": 1800
            },
            {
                "name": "Protocol",
                "url": "https://www.protocol.com/",
                "source_type": "blog",
                "description": "Tech news and analysis from the people behind the news",
                "update_interval": 3600
            },
            {
                "name": "The Verge",
                "url": "https://www.theverge.com/",
                "source_type": "blog",
                "description": "Technology, science, art, and culture coverage",
                "update_interval": 1800
            },
            {
                "name": "Wired",
                "url": "https://www.wired.com/",
                "source_type": "blog",
                "description": "Technology, science, and culture magazine",
                "update_interval": 3600
            },
            {
                "name": "MIT Technology Review",
                "url": "https://www.technologyreview.com/",
                "source_type": "blog",
                "description": "Insights on emerging technologies and their commercial, social, and political impacts",
                "update_interval": 7200
            },
            
            # PODCASTS
            {
                "name": "All-In Podcast",
                "url": "https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk",
                "source_type": "podcast",
                "description": "Weekly podcast covering business, technology, and current events",
                "update_interval": 86400
            },
            {
                "name": "Collin Samir Podcast",
                "url": "https://open.spotify.com/show/0Q86acNRm6V9GYx55SXKwf",
                "source_type": "podcast",
                "description": "Creator economy and business insights",
                "update_interval": 86400
            },
            {
                "name": "Masters of Scale",
                "url": "https://open.spotify.com/show/1rMA13GjwjVftEe4ndh7Hm",
                "source_type": "podcast",
                "description": "Reid Hoffman's podcast on scaling businesses",
                "update_interval": 86400
            },
            {
                "name": "How I Built This",
                "url": "https://open.spotify.com/show/6E709HRH7XaiZrMfgtkfun",
                "source_type": "podcast",
                "description": "Stories behind some of the world's best known companies",
                "update_interval": 86400
            },
            {
                "name": "The Tim Ferriss Show",
                "url": "https://open.spotify.com/show/5qSUyCrWzdurrhD0hPJIN7",
                "source_type": "podcast",
                "description": "Interviews with world-class performers",
                "update_interval": 86400
            },
            {
                "name": "Lex Fridman Podcast",
                "url": "https://open.spotify.com/show/2MAi0BvJcGYt5YEVXiw7yq",
                "source_type": "podcast",
                "description": "Conversations about science, technology, history, philosophy and nature",
                "update_interval": 86400
            },
            {
                "name": "The Joe Rogan Experience",
                "url": "https://open.spotify.com/show/38bS44xjbVVZ3No3XiF9sy",
                "source_type": "podcast",
                "description": "Long form conversations with interesting people",
                "update_interval": 86400
            },
            {
                "name": "Invest Like the Best",
                "url": "https://open.spotify.com/show/0eUUeH2WirtxG8o1POQiqa",
                "source_type": "podcast",
                "description": "Conversations with the best investors and business leaders",
                "update_interval": 86400
            },
            {
                "name": "The Knowledge Project",
                "url": "https://open.spotify.com/show/1nARKz2vTIOb7gH9ihhs45",
                "source_type": "podcast",
                "description": "Shane Parrish's podcast on mental models and decision making",
                "update_interval": 86400
            },
            {
                "name": "Acquired",
                "url": "https://open.spotify.com/show/7Fj0XEuRQLUo7MkqvOuMng",
                "source_type": "podcast",
                "description": "Stories of great companies and how they were built",
                "update_interval": 86400
            },
            
            # TWITTER INFLUENCERS
            {
                "name": "Twitter - @naval",
                "url": "https://twitter.com/naval",
                "source_type": "twitter",
                "description": "Naval Ravikant's insights on business and life",
                "update_interval": 3600
            },
            {
                "name": "Twitter - @paulg",
                "url": "https://twitter.com/paulg",
                "source_type": "twitter",
                "description": "Paul Graham's thoughts on startups and technology",
                "update_interval": 3600
            },
            {
                "name": "Twitter - @pmarca",
                "url": "https://twitter.com/pmarca",
                "source_type": "twitter",
                "description": "Marc Andreessen's insights on technology and business",
                "update_interval": 3600
            },
            {
                "name": "Twitter - @elonmusk",
                "url": "https://twitter.com/elonmusk",
                "source_type": "twitter",
                "description": "Elon Musk's updates on Tesla, SpaceX, and technology",
                "update_interval": 1800
            },
            {
                "name": "Twitter - @sama",
                "url": "https://twitter.com/sama",
                "source_type": "twitter",
                "description": "Sam Altman's thoughts on AI and technology",
                "update_interval": 3600
            },
            {
                "name": "Twitter - @patrickc",
                "url": "https://twitter.com/patrickc",
                "source_type": "twitter",
                "description": "Patrick Collison's insights on business and technology",
                "update_interval": 3600
            },
            {
                "name": "Twitter - @balajis",
                "url": "https://twitter.com/balajis",
                "source_type": "twitter",
                "description": "Balaji Srinivasan's thoughts on technology and society",
                "update_interval": 3600
            },
            {
                "name": "Twitter - @cdixon",
                "url": "https://twitter.com/cdixon",
                "source_type": "twitter",
                "description": "Chris Dixon's insights on crypto and technology",
                "update_interval": 3600
            },
            {
                "name": "Twitter - @bhorowitz",
                "url": "https://twitter.com/bhorowitz",
                "source_type": "twitter",
                "description": "Ben Horowitz's thoughts on business and leadership",
                "update_interval": 3600
            },
            {
                "name": "Twitter - @fchollet",
                "url": "https://twitter.com/fchollet",
                "source_type": "twitter",
                "description": "François Chollet's insights on AI and machine learning",
                "update_interval": 3600
            },
            
            # REDDIT COMMUNITIES
            {
                "name": "Reddit - r/Entrepreneur",
                "url": "https://www.reddit.com/r/Entrepreneur/",
                "source_type": "reddit",
                "description": "Entrepreneurship and business discussions",
                "update_interval": 1800
            },
            {
                "name": "Reddit - r/startups",
                "url": "https://www.reddit.com/r/startups/",
                "source_type": "reddit",
                "description": "Startup community discussions and insights",
                "update_interval": 1800
            },
            {
                "name": "Reddit - r/technology",
                "url": "https://www.reddit.com/r/technology/",
                "source_type": "reddit",
                "description": "Technology news and discussions",
                "update_interval": 1800
            },
            {
                "name": "Reddit - r/investing",
                "url": "https://www.reddit.com/r/investing/",
                "source_type": "reddit",
                "description": "Investment strategies and market discussions",
                "update_interval": 1800
            },
            {
                "name": "Reddit - r/artificial",
                "url": "https://www.reddit.com/r/artificial/",
                "source_type": "reddit",
                "description": "AI and machine learning discussions",
                "update_interval": 1800
            },
            {
                "name": "Reddit - r/cryptocurrency",
                "url": "https://www.reddit.com/r/cryptocurrency/",
                "source_type": "reddit",
                "description": "Cryptocurrency news and discussions",
                "update_interval": 1800
            },
            {
                "name": "Reddit - r/business",
                "url": "https://www.reddit.com/r/business/",
                "source_type": "reddit",
                "description": "Business news and discussions",
                "update_interval": 1800
            },
            {
                "name": "Reddit - r/economics",
                "url": "https://www.reddit.com/r/economics/",
                "source_type": "reddit",
                "description": "Economic theory and current events",
                "update_interval": 1800
            },
            {
                "name": "Reddit - r/venturecapital",
                "url": "https://www.reddit.com/r/venturecapital/",
                "source_type": "reddit",
                "description": "Venture capital and startup funding discussions",
                "update_interval": 1800
            },
            {
                "name": "Reddit - r/consulting",
                "url": "https://www.reddit.com/r/consulting/",
                "source_type": "reddit",
                "description": "Management consulting industry discussions",
                "update_interval": 1800
            },
            
            # VC FUNDS & REPORTS
            {
                "name": "Sequoia Capital Blog",
                "url": "https://www.sequoiacap.com/insights/",
                "source_type": "blog",
                "description": "Sequoia Capital's insights on technology and business",
                "update_interval": 7200
            },
            {
                "name": "Benchmark Blog",
                "url": "https://benchmark.com/blog/",
                "source_type": "blog",
                "description": "Benchmark Capital's thoughts on technology and business",
                "update_interval": 7200
            },
            {
                "name": "Greylock Blog",
                "url": "https://greylock.com/perspectives/",
                "source_type": "blog",
                "description": "Greylock Partners' insights on technology and business",
                "update_interval": 7200
            },
            {
                "name": "First Round Review",
                "url": "https://firstround.com/review/",
                "source_type": "blog",
                "description": "First Round Capital's insights on startups and business",
                "update_interval": 7200
            },
            {
                "name": "Union Square Ventures Blog",
                "url": "https://www.usv.com/blog",
                "source_type": "blog",
                "description": "Union Square Ventures' thoughts on technology and business",
                "update_interval": 7200
            },
            {
                "name": "Index Ventures Blog",
                "url": "https://www.indexventures.com/insights",
                "source_type": "blog",
                "description": "Index Ventures' insights on technology and business",
                "update_interval": 7200
            },
            {
                "name": "Accel Blog",
                "url": "https://www.accel.com/insights",
                "source_type": "blog",
                "description": "Accel's thoughts on technology and business",
                "update_interval": 7200
            },
            {
                "name": "Kleiner Perkins Blog",
                "url": "https://www.kleinerperkins.com/perspectives",
                "source_type": "blog",
                "description": "Kleiner Perkins' insights on technology and business",
                "update_interval": 7200
            },
            {
                "name": "Tiger Global Blog",
                "url": "https://www.tigerglobal.com/insights",
                "source_type": "blog",
                "description": "Tiger Global's thoughts on technology and business",
                "update_interval": 7200
            },
            {
                "name": "SoftBank Vision Fund",
                "url": "https://group.softbank/en/vision-fund/",
                "source_type": "blog",
                "description": "SoftBank Vision Fund's insights on technology and business",
                "update_interval": 7200
            },
            
            # CREATOR ECONOMY
            {
                "name": "Creator Economy Newsletter",
                "url": "https://creatoreconomy.substack.com/",
                "source_type": "blog",
                "description": "News and insights on the creator economy",
                "update_interval": 86400
            },
            {
                "name": "Creator Economy Hub",
                "url": "https://www.creatoreconomyhub.com/",
                "source_type": "blog",
                "description": "Resources and insights for creators",
                "update_interval": 86400
            },
            {
                "name": "Patreon Blog",
                "url": "https://blog.patreon.com/",
                "source_type": "blog",
                "description": "Patreon's insights on creator monetization",
                "update_interval": 86400
            },
            {
                "name": "OnlyFans Blog",
                "url": "https://blog.onlyfans.com/",
                "source_type": "blog",
                "description": "OnlyFans' insights on creator platforms",
                "update_interval": 86400
            },
            {
                "name": "TikTok Creator Portal",
                "url": "https://www.tiktok.com/business/en/creator-portal",
                "source_type": "blog",
                "description": "TikTok's creator resources and insights",
                "update_interval": 86400
            },
            {
                "name": "YouTube Creator Blog",
                "url": "https://youtube-creators.googleblog.com/",
                "source_type": "blog",
                "description": "YouTube's insights for creators",
                "update_interval": 86400
            },
            {
                "name": "Twitch Blog",
                "url": "https://blog.twitch.tv/",
                "source_type": "blog",
                "description": "Twitch's insights for streamers and creators",
                "update_interval": 86400
            },
            {
                "name": "Instagram Creator Blog",
                "url": "https://about.instagram.com/blog/topics/creator",
                "source_type": "blog",
                "description": "Instagram's insights for creators",
                "update_interval": 86400
            },
            {
                "name": "Twitter Creator Blog",
                "url": "https://blog.twitter.com/en_us/topics/creator",
                "source_type": "blog",
                "description": "Twitter's insights for creators",
                "update_interval": 86400
            },
            {
                "name": "LinkedIn Creator Blog",
                "url": "https://www.linkedin.com/help/linkedin/answer/a1337",
                "source_type": "blog",
                "description": "LinkedIn's insights for creators",
                "update_interval": 86400
            }
        ]
        
        # Clear existing sources first to avoid duplicates
        print("🗑️  Clearing existing sources...")
        db.query(Source).delete()
        db.commit()
        print("✅ Existing sources cleared")
        
        # Add new sources
        for source_data in sample_sources:
            source = Source(**source_data)
            db.add(source)
            print(f"✅ Added source: {source_data['name']}")
        
        # Create sample user
        sample_user = db.query(User).filter(User.email == "demo@mediamonitor.com").first()
        if not sample_user:
            user = User(
                email="demo@mediamonitor.com",
                username="demo_user"
            )
            db.add(user)
            print("✅ Added demo user: demo@mediamonitor.com")
        else:
            print("⏭️  Demo user already exists")
        
        db.commit()
        print(f"\n🎉 Database initialization completed successfully!")
        print(f"📊 Total sources added: {len(sample_sources)}")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Main function to initialize the database."""
    print("🗄️  Initializing Media Monitor Database...")
    
    try:
        # Initialize database tables first
        init_db()
        print("✅ Database tables created successfully")
        
        # Wait a moment to ensure tables are fully created
        import time
        time.sleep(1)
        
        # Create sample data
        create_sample_data()
        
        print("\n🚀 You can now start the application with: python main.py")
        print("📊 Access the dashboard at: http://localhost:8000")
        print("🔧 API docs at: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
