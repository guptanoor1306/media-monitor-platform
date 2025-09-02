from typing import List, Optional
from datetime import datetime
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import feedparser
from urllib.parse import urlparse
from src.scrapers.base_scraper import BaseScraper
from src.models import Content
from src.config import settings
from bs4 import BeautifulSoup
from urllib.parse import urljoin


class PodcastScraper(BaseScraper):
    """Scraper for podcast content from Spotify and RSS feeds."""
    
    def __init__(self):
        super().__init__()
        self.spotify = None
        self._init_spotify_api()
    
    def _init_spotify_api(self):
        """Initialize Spotify API client."""
        try:
            if settings.spotify_client_id and settings.spotify_client_secret:
                client_credentials_manager = SpotifyClientCredentials(
                    client_id=settings.spotify_client_id,
                    client_secret=settings.spotify_client_secret
                )
                self.spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        except Exception as e:
            print(f"Error initializing Spotify API: {e}")
    
    def scrape_content(self, source_url: str) -> List[Content]:
        """Scrape content from a podcast source."""
        contents = []
        
        try:
            # Determine source type and scrape accordingly
            if 'spotify.com' in source_url:
                contents.extend(self._scrape_spotify_podcast(source_url))
            elif self._is_rss_feed(source_url):
                contents.extend(self._scrape_rss_podcast(source_url))
            else:
                # Try to find RSS feed for the podcast
                rss_url = self._find_podcast_rss(source_url)
                if rss_url:
                    contents.extend(self._scrape_rss_podcast(rss_url))
            
        except Exception as e:
            print(f"Error scraping podcast {source_url}: {e}")
        
        return contents
    
    def _is_rss_feed(self, url: str) -> bool:
        """Check if URL is an RSS feed."""
        try:
            response = self.session.head(url, timeout=5)
            content_type = response.headers.get('content-type', '').lower()
            return 'xml' in content_type or 'rss' in content_type
        except:
            return False
    
    def _scrape_spotify_podcast(self, url: str) -> List[Content]:
        """Scrape podcast episodes from Spotify."""
        contents = []
        
        if not self.spotify:
            print("Spotify API not initialized")
            return contents
        
        try:
            # Extract show ID from URL
            show_id = self._extract_spotify_show_id(url)
            if not show_id:
                return contents
            
            # Get show details
            show = self.spotify.show(show_id)
            show_name = show['name']
            
            # Get episodes
            episodes = self.spotify.show_episodes(show_id, limit=50)
            
            for episode in episodes['items']:
                try:
                    # Extract episode details
                    title = episode['name']
                    description = episode['description'][:500] if episode['description'] else None
                    
                    # Get episode URL
                    episode_url = episode['external_urls']['spotify']
                    
                    # Extract thumbnail
                    thumbnail = episode['images'][0]['url'] if episode['images'] else None
                    
                    # Extract published date
                    published_at = datetime.fromisoformat(episode['release_date'].replace('Z', '+00:00'))
                    
                    # Extract duration
                    duration_ms = episode['duration_ms']
                    duration_minutes = round(duration_ms / 60000, 1)
                    
                    # Extract tags
                    tags = self._extract_tags(None, title, description or "") + [show_name, "podcast", "spotify"]
                    if episode.get('explicit'):
                        tags.append("explicit")
                    
                    content = Content(
                        title=title,
                        description=description,
                        content_url=episode_url,
                        content_text=description,
                        thumbnail_url=thumbnail,
                        published_at=published_at,
                        author=show_name,
                        tags=tags,
                        engagement_metrics={
                            'duration_minutes': duration_minutes,
                            'explicit': episode.get('explicit', False)
                        },
                        source_id=None
                    )
                    contents.append(content)
                    
                except Exception as e:
                    print(f"Error parsing Spotify episode: {e}")
                    continue
            
        except Exception as e:
            print(f"Error scraping Spotify podcast {url}: {e}")
        
        return contents
    
    def _extract_spotify_show_id(self, url: str) -> Optional[str]:
        """Extract Spotify show ID from URL."""
        import re
        match = re.search(r'/show/([a-zA-Z0-9]+)', url)
        return match.group(1) if match else None
    
    def _scrape_rss_podcast(self, rss_url: str) -> List[Content]:
        """Scrape podcast episodes from RSS feed."""
        contents = []
        
        try:
            # Parse RSS feed
            feed = feedparser.parse(rss_url)
            
            for entry in feed.entries:
                try:
                    # Extract episode details
                    title = entry.get('title', '').strip()
                    if not title:
                        continue
                    
                    description = entry.get('summary', '').strip()
                    if description:
                        description = description[:500]
                    
                    # Get episode URL
                    episode_url = entry.get('link', '')
                    if not episode_url:
                        continue
                    
                    # Extract thumbnail
                    thumbnail = None
                    if entry.get('media_content'):
                        for media in entry.media_content:
                            if media.get('medium') == 'image':
                                thumbnail = media.get('url')
                                break
                    elif entry.get('media_thumbnail'):
                        thumbnail = entry.media_thumbnail[0].get('url')
                    
                    # Extract published date
                    published_at = None
                    if entry.get('published_parsed'):
                        published_at = datetime(*entry.published_parsed[:6])
                    
                    # Extract author
                    author = entry.get('author', '')
                    if not author and feed.feed.get('title'):
                        author = feed.feed.title
                    
                    # Extract duration
                    duration = None
                    if entry.get('media_content'):
                        for media in entry.media_content:
                            if media.get('medium') == 'audio':
                                duration = media.get('duration')
                                break
                    
                    # Extract tags
                    tags = self._extract_tags(None, title, description or "") + ["podcast", "rss"]
                    if author:
                        tags.append(author)
                    
                    content = Content(
                        title=title,
                        description=description,
                        content_url=episode_url,
                        content_text=description,
                        thumbnail_url=thumbnail,
                        published_at=published_at,
                        author=author,
                        tags=tags,
                        engagement_metrics={
                            'duration': duration
                        },
                        source_id=None
                    )
                    contents.append(content)
                    
                except Exception as e:
                    print(f"Error parsing RSS podcast entry: {e}")
                    continue
            
        except Exception as e:
            print(f"Error scraping RSS podcast {rss_url}: {e}")
        
        return contents
    
    def _find_podcast_rss(self, url: str) -> Optional[str]:
        """Find RSS feed URL for a podcast website."""
        try:
            html = self._get_page_content(url)
            if not html:
                return None
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Look for RSS feed links
            rss_links = soup.find_all('link', rel='alternate')
            for link in rss_links:
                if 'rss' in link.get('type', '') or 'xml' in link.get('type', ''):
                    return urljoin(url, link.get('href'))
            
            # Try common podcast RSS URLs
            common_rss = [
                '/feed/podcast',
                '/podcast/feed',
                '/rss',
                '/feed.xml',
                '/podcast.xml'
            ]
            
            for rss_path in common_rss:
                rss_url = urljoin(url, rss_path)
                try:
                    response = self.session.head(rss_url, timeout=5)
                    if response.status_code == 200:
                        return rss_url
                except:
                    continue
            
            return None
            
        except Exception as e:
            print(f"Error finding podcast RSS for {url}: {e}")
            return None
    
    def search_podcasts(self, query: str, limit: int = 10) -> List[dict]:
        """Search for podcasts on Spotify."""
        if not self.spotify:
            return []
        
        try:
            results = self.spotify.search(q=query, type='show', limit=limit)
            podcasts = []
            
            for show in results['shows']['items']:
                podcast = {
                    'id': show['id'],
                    'name': show['name'],
                    'description': show['description'],
                    'thumbnail': show['images'][0]['url'] if show['images'] else None,
                    'url': show['external_urls']['spotify'],
                    'publisher': show['publisher'],
                    'total_episodes': show['total_episodes']
                }
                podcasts.append(podcast)
            
            return podcasts
            
        except Exception as e:
            print(f"Error searching podcasts: {e}")
            return []
