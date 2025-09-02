from typing import List, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import feedparser
from src.scrapers.base_scraper import BaseScraper
from src.models import Content


class BlogScraper(BaseScraper):
    """Scraper for blog platforms like Substack, news sites, etc."""
    
    def __init__(self):
        super().__init__()
        self.feed_parsers = {
            'substack': self._scrape_substack,
            'rss': self._scrape_rss_feed,
            'generic': self._scrape_generic_blog
        }
    
    def scrape_content(self, source_url: str) -> List[Content]:
        """Scrape content from a blog source."""
        # Determine the type of blog and use appropriate scraper
        blog_type = self._detect_blog_type(source_url)
        scraper_method = self.feed_parsers.get(blog_type, self._scrape_generic_blog)
        
        try:
            return scraper_method(source_url)
        except Exception as e:
            print(f"Error scraping {source_url}: {e}")
            return []
    
    def _detect_blog_type(self, url: str) -> str:
        """Detect the type of blog platform."""
        domain = urlparse(url).netloc.lower()
        
        if 'substack.com' in domain:
            return 'substack'
        elif self._has_rss_feed(url):
            return 'rss'
        else:
            return 'generic'
    
    def _has_rss_feed(self, url: str) -> bool:
        """Check if the blog has an RSS feed."""
        try:
            # Common RSS feed URLs
            rss_urls = [
                urljoin(url, '/feed'),
                urljoin(url, '/rss'),
                urljoin(url, '/feed.xml'),
                urljoin(url, '/rss.xml'),
                urljoin(url, '/atom.xml')
            ]
            
            for rss_url in rss_urls:
                response = self.session.head(rss_url, timeout=5)
                if response.status_code == 200:
                    return True
            return False
        except:
            return False
    
    def _scrape_substack(self, url: str) -> List[Content]:
        """Scrape content from Substack newsletters."""
        contents = []
        
        try:
            # Substack has a specific structure
            html = self._get_page_content(url, use_selenium=True)
            if not html:
                return contents
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find newsletter posts
            posts = soup.find_all('article') or soup.find_all('.post-preview')
            
            for post in posts:
                try:
                    # Extract title
                    title_elem = post.find('h1') or post.find('h2') or post.find('.post-title')
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    
                    # Extract description
                    desc_elem = post.find('.post-excerpt') or post.find('.post-description')
                    description = desc_elem.get_text(strip=True) if desc_elem else None
                    
                    # Extract link
                    link_elem = post.find('a')
                    if not link_elem:
                        continue
                    post_url = urljoin(url, link_elem.get('href'))
                    
                    # Extract thumbnail
                    thumbnail = self._extract_thumbnail(post, post_url)
                    
                    # Extract author
                    author = self._extract_author(post)
                    
                    # Extract date
                    published_at = self._extract_published_date(post)
                    
                    # Extract tags
                    tags = self._extract_tags(post, title, description or "")
                    
                    content = Content(
                        title=title,
                        description=description,
                        content_url=post_url,
                        thumbnail_url=thumbnail,
                        author=author,
                        published_at=published_at,
                        tags=tags,
                        source_id=None  # Will be set by caller
                    )
                    contents.append(content)
                    
                except Exception as e:
                    print(f"Error parsing post: {e}")
                    continue
            
        except Exception as e:
            print(f"Error scraping Substack {url}: {e}")
        
        return contents
    
    def _scrape_rss_feed(self, url: str) -> List[Content]:
        """Scrape content from RSS feeds."""
        contents = []
        
        try:
            # Find RSS feed URL
            rss_url = self._find_rss_url(url)
            if not rss_url:
                return contents
            
            # Parse RSS feed
            feed = feedparser.parse(rss_url)
            
            for entry in feed.entries:
                try:
                    # Extract title
                    title = entry.get('title', '').strip()
                    if not title:
                        continue
                    
                    # Extract description
                    description = entry.get('summary', '').strip()
                    
                    # Extract link
                    post_url = entry.get('link', '')
                    if not post_url:
                        continue
                    
                    # Extract published date
                    published_at = None
                    if entry.get('published_parsed'):
                        from datetime import datetime
                        published_at = datetime(*entry.published_parsed[:6])
                    
                    # Extract author
                    author = entry.get('author', '')
                    
                    # Extract tags
                    tags = []
                    if entry.get('tags'):
                        tags = [tag.term for tag in entry.tags]
                    
                    # Try to get thumbnail from media content
                    thumbnail = None
                    if entry.get('media_content'):
                        thumbnail = entry.media_content[0].get('url')
                    elif entry.get('media_thumbnail'):
                        thumbnail = entry.media_thumbnail[0].get('url')
                    
                    content = Content(
                        title=title,
                        description=description,
                        content_url=post_url,
                        thumbnail_url=thumbnail,
                        author=author,
                        published_at=published_at,
                        tags=tags,
                        source_id=None  # Will be set by caller
                    )
                    contents.append(content)
                    
                except Exception as e:
                    print(f"Error parsing RSS entry: {e}")
                    continue
            
        except Exception as e:
            print(f"Error scraping RSS feed {url}: {e}")
        
        return contents
    
    def _find_rss_url(self, url: str) -> Optional[str]:
        """Find the RSS feed URL for a blog."""
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
            
            # Try common RSS URLs
            common_rss = ['/feed', '/rss', '/feed.xml', '/rss.xml', '/atom.xml']
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
            print(f"Error finding RSS URL for {url}: {e}")
            return None
    
    def _scrape_generic_blog(self, url: str) -> List[Content]:
        """Scrape content from generic blog platforms."""
        contents = []
        
        try:
            html = self._get_page_content(url, use_selenium=True)
            if not html:
                return contents
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Try to find blog posts using common selectors
            post_selectors = [
                '.post', '.article', '.entry', '.blog-post',
                '[class*="post"]', '[class*="article"]', '[class*="entry"]'
            ]
            
            posts = []
            for selector in post_selectors:
                posts = soup.select(selector)
                if posts:
                    break
            
            if not posts:
                # Fallback: look for any article-like content
                posts = soup.find_all(['article', 'div'], class_=lambda x: x and any(word in x.lower() for word in ['post', 'article', 'entry']))
            
            for post in posts[:20]:  # Limit to 20 posts
                try:
                    # Extract title
                    title_elem = post.find(['h1', 'h2', 'h3'])
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    
                    # Extract description
                    desc_elem = post.find(['p', '.excerpt', '.summary'])
                    description = desc_elem.get_text(strip=True) if desc_elem else None
                    
                    # Extract link
                    link_elem = post.find('a')
                    if not link_elem:
                        continue
                    post_url = urljoin(url, link_elem.get('href'))
                    
                    # Extract thumbnail
                    thumbnail = self._extract_thumbnail(post, post_url)
                    
                    # Extract author
                    author = self._extract_author(post)
                    
                    # Extract date
                    published_at = self._extract_published_date(post)
                    
                    # Extract tags
                    tags = self._extract_tags(post, title, description or "")
                    
                    content = Content(
                        title=title,
                        description=description,
                        content_url=post_url,
                        thumbnail_url=thumbnail,
                        author=author,
                        published_at=published_at,
                        tags=tags,
                        source_id=None  # Will be set by caller
                    )
                    contents.append(content)
                    
                except Exception as e:
                    print(f"Error parsing generic post: {e}")
                    continue
            
        except Exception as e:
            print(f"Error scraping generic blog {url}: {e}")
        
        return contents
