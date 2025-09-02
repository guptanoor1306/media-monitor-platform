from typing import List, Optional
from datetime import datetime
import tweepy
import praw
from src.scrapers.base_scraper import BaseScraper
from src.models import Content
from src.config import settings


class TwitterScraper(BaseScraper):
    """Scraper for Twitter content."""
    
    def __init__(self):
        super().__init__()
        self.api = None
        self._init_twitter_api()
    
    def _init_twitter_api(self):
        """Initialize Twitter API client."""
        try:
            if all([settings.twitter_api_key, settings.twitter_api_secret, 
                   settings.twitter_access_token, settings.twitter_access_token_secret]):
                auth = tweepy.OAuthHandler(settings.twitter_api_key, settings.twitter_api_secret)
                auth.set_access_token(settings.twitter_access_token, settings.twitter_access_token_secret)
                self.api = tweepy.API(auth, wait_on_rate_limit=True)
            elif settings.twitter_bearer_token:
                self.api = tweepy.Client(bearer_token=settings.twitter_bearer_token)
        except Exception as e:
            print(f"Error initializing Twitter API: {e}")
    
    def scrape_content(self, source_url: str) -> List[Content]:
        """Scrape content from Twitter source (username or hashtag)."""
        if not self.api:
            print("Twitter API not initialized")
            return []
        
        contents = []
        
        try:
            # Extract username or hashtag from URL
            if '/user/' in source_url or '/@' in source_url:
                username = self._extract_username(source_url)
                if username:
                    contents.extend(self._scrape_user_tweets(username))
            elif '/hashtag/' in source_url:
                hashtag = self._extract_hashtag(source_url)
                if hashtag:
                    contents.extend(self._scrape_hashtag_tweets(hashtag))
            
        except Exception as e:
            print(f"Error scraping Twitter {source_url}: {e}")
        
        return contents
    
    def _extract_username(self, url: str) -> Optional[str]:
        """Extract username from Twitter URL."""
        import re
        match = re.search(r'/(?:user/|@)([^/]+)', url)
        return match.group(1) if match else None
    
    def _extract_hashtag(self, url: str) -> Optional[str]:
        """Extract hashtag from Twitter URL."""
        import re
        match = re.search(r'/hashtag/([^/?]+)', url)
        return match.group(1) if match else None
    
    def _scrape_user_tweets(self, username: str) -> List[Content]:
        """Scrape tweets from a specific user."""
        contents = []
        
        try:
            # Get user's recent tweets
            tweets = self.api.user_timeline(
                screen_name=username,
                count=50,  # Get last 50 tweets
                tweet_mode='extended'
            )
            
            for tweet in tweets:
                try:
                    # Skip retweets and replies if they have low engagement
                    if hasattr(tweet, 'retweeted_status') or tweet.in_reply_to_status_id:
                        if tweet.favorite_count < 10:  # Low engagement threshold
                            continue
                    
                    # Create content object
                    content = Content(
                        title=f"Tweet by @{username}",
                        description=tweet.full_text[:500],  # Truncate long tweets
                        content_url=f"https://twitter.com/{username}/status/{tweet.id}",
                        content_text=tweet.full_text,
                        published_at=tweet.created_at,
                        author=username,
                        tags=self._extract_tags(None, tweet.text, tweet.text) + [f"@{username}", "twitter"],
                        engagement_metrics={
                            'likes': tweet.favorite_count,
                            'retweets': tweet.retweet_count,
                            'replies': getattr(tweet, 'reply_count', 0)
                        },
                        source_id=None
                    )
                    contents.append(content)
                    
                except Exception as e:
                    print(f"Error parsing tweet: {e}")
                    continue
            
        except Exception as e:
            print(f"Error scraping user tweets for {username}: {e}")
        
        return contents
    
    def _scrape_hashtag_tweets(self, hashtag: str) -> List[Content]:
        """Scrape tweets with a specific hashtag."""
        contents = []
        
        try:
            # Search for tweets with hashtag
            query = f"#{hashtag} -filter:retweets"
            tweets = tweepy.Cursor(
                self.api.search_tweets,
                q=query,
                tweet_mode='extended',
                lang='en'
            ).items(100)
            
            for tweet in tweets:
                try:
                    # Only include tweets with high engagement
                    if tweet.favorite_count < 20:  # Higher threshold for hashtag tweets
                        continue
                    
                    content = Content(
                        title=f"#{hashtag} Tweet",
                        description=tweet.full_text[:500],
                        content_url=f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}",
                        content_text=tweet.full_text,
                        published_at=tweet.created_at,
                        author=tweet.user.screen_name,
                        tags=self._extract_tags(None, tweet.text, tweet.text) + [f"#{hashtag}", "twitter", f"@{tweet.user.screen_name}"],
                        engagement_metrics={
                            'likes': tweet.favorite_count,
                            'retweets': tweet.retweet_count,
                            'replies': getattr(tweet, 'reply_count', 0)
                        },
                        source_id=None
                    )
                    contents.append(content)
                    
                except Exception as e:
                    print(f"Error parsing hashtag tweet: {e}")
                    continue
            
        except Exception as e:
            print(f"Error scraping hashtag tweets for #{hashtag}: {e}")
        
        return contents


class RedditScraper(BaseScraper):
    """Scraper for Reddit content."""
    
    def __init__(self):
        super().__init__()
        self.reddit = None
        self._init_reddit_api()
    
    def _init_reddit_api(self):
        """Initialize Reddit API client."""
        try:
            if settings.reddit_client_id and settings.reddit_client_secret:
                self.reddit = praw.Reddit(
                    client_id=settings.reddit_client_id,
                    client_secret=settings.reddit_client_secret,
                    user_agent=settings.reddit_user_agent
                )
        except Exception as e:
            print(f"Error initializing Reddit API: {e}")
    
    def scrape_content(self, source_url: str) -> List[Content]:
        """Scrape content from Reddit source (subreddit or user)."""
        if not self.reddit:
            print("Reddit API not initialized")
            return []
        
        contents = []
        
        try:
            if '/r/' in source_url:
                subreddit_name = self._extract_subreddit(source_url)
                if subreddit_name:
                    contents.extend(self._scrape_subreddit(subreddit_name))
            elif '/u/' in source_url or '/user/' in source_url:
                username = self._extract_reddit_username(source_url)
                if username:
                    contents.extend(self._scrape_user_posts(username))
            
        except Exception as e:
            print(f"Error scraping Reddit {source_url}: {e}")
        
        return contents
    
    def _extract_subreddit(self, url: str) -> Optional[str]:
        """Extract subreddit name from URL."""
        import re
        match = re.search(r'/r/([^/]+)', url)
        return match.group(1) if match else None
    
    def _extract_reddit_username(self, url: str) -> Optional[str]:
        """Extract Reddit username from URL."""
        import re
        match = re.search(r'/(?:u/|user/)([^/]+)', url)
        return match.group(1) if match else None
    
    def _scrape_subreddit(self, subreddit_name: str) -> List[Content]:
        """Scrape posts from a subreddit."""
        contents = []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Get hot posts
            for post in subreddit.hot(limit=50):
                try:
                    # Skip low-quality posts
                    if post.score < 10:
                        continue
                    
                    # Extract content
                    title = post.title
                    description = post.selftext[:500] if post.selftext else None
                    
                    # Get post URL
                    if post.is_self:
                        content_url = f"https://reddit.com{post.permalink}"
                    else:
                        content_url = post.url
                    
                    # Extract thumbnail
                    thumbnail = None
                    if hasattr(post, 'thumbnail') and post.thumbnail != 'default':
                        thumbnail = post.thumbnail
                    elif hasattr(post, 'preview') and post.preview.get('images'):
                        thumbnail = post.preview['images'][0]['source']['url']
                    
                    content = Content(
                        title=title,
                        description=description,
                        content_url=content_url,
                        content_text=post.selftext,
                        thumbnail_url=thumbnail,
                        published_at=datetime.fromtimestamp(post.created_utc),
                        author=str(post.author),
                        tags=self._extract_tags(None, post.title, post.selftext or "") + [f"r/{subreddit_name}", "reddit"],
                        engagement_metrics={
                            'upvotes': post.score,
                            'comments': post.num_comments,
                            'ratio': post.upvote_ratio
                        },
                        source_id=None
                    )
                    contents.append(content)
                    
                except Exception as e:
                    print(f"Error parsing Reddit post: {e}")
                    continue
            
        except Exception as e:
            print(f"Error scraping subreddit r/{subreddit_name}: {e}")
        
        return contents
    
    def _scrape_user_posts(self, username: str) -> List[Content]:
        """Scrape posts from a Reddit user."""
        contents = []
        
        try:
            user = self.reddit.redditor(username)
            
            # Get user's top posts
            for post in user.top(limit=50):
                try:
                    # Skip low-quality posts
                    if post.score < 5:
                        continue
                    
                    title = post.title
                    description = post.selftext[:500] if post.selftext else None
                    
                    if post.is_self:
                        content_url = f"https://reddit.com{post.permalink}"
                    else:
                        content_url = post.url
                    
                    # Extract thumbnail
                    thumbnail = None
                    if hasattr(post, 'thumbnail') and post.thumbnail != 'default':
                        thumbnail = post.thumbnail
                    elif hasattr(post, 'preview') and post.preview.get('images'):
                        thumbnail = post.preview['images'][0]['source']['url']
                    
                    content = Content(
                        title=title,
                        description=description,
                        content_url=content_url,
                        content_text=post.selftext,
                        thumbnail_url=thumbnail,
                        published_at=datetime.fromtimestamp(post.created_utc),
                        author=username,
                        tags=[f"u/{username}", "reddit"],
                        engagement_metrics={
                            'upvotes': post.score,
                            'comments': post.num_comments,
                            'ratio': post.upvote_ratio
                        },
                        source_id=None
                    )
                    contents.append(content)
                    
                except Exception as e:
                    print(f"Error parsing user post: {e}")
                    continue
            
        except Exception as e:
            print(f"Error scraping user posts for u/{username}: {e}")
        
        return contents
