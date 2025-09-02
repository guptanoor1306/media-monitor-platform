from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.config import settings
from src.models import Content


class BaseScraper(ABC):
    """Base class for all content scrapers."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.driver = None
        
    def _get_selenium_driver(self):
        """Get Selenium WebDriver for JavaScript-heavy sites."""
        if not self.driver:
            chrome_options = Options()
            if settings.selenium_headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            self.driver = webdriver.Chrome(options=chrome_options)
        return self.driver
    
    def _get_page_content(self, url: str, use_selenium: bool = False) -> Optional[str]:
        """Get page content using requests or Selenium."""
        try:
            if use_selenium:
                driver = self._get_selenium_driver()
                driver.get(url)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                return driver.page_source
            else:
                response = self.session.get(url, timeout=settings.request_timeout)
                response.raise_for_status()
                return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def _extract_thumbnail(self, soup: BeautifulSoup, url: str) -> Optional[str]:
        """Extract thumbnail URL from page."""
        # Try Open Graph image first
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            return og_image['content']
        
        # Try Twitter image
        twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
        if twitter_image and twitter_image.get('content'):
            return twitter_image['content']
        
        # Try to find any image
        img = soup.find('img')
        if img and img.get('src'):
            src = img['src']
            if src.startswith('//'):
                src = 'https:' + src
            elif src.startswith('/'):
                # Handle relative URLs
                from urllib.parse import urljoin
                src = urljoin(url, src)
            return src
        
        return None
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author information from page."""
        # Try various author selectors
        author_selectors = [
            'meta[name="author"]',
            'meta[property="article:author"]',
            '.author',
            '.byline',
            '[rel="author"]'
        ]
        
        for selector in author_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    return element.get('content')
                else:
                    return element.get_text(strip=True)
        
        return None
    
    def _extract_tags(self, soup: BeautifulSoup, title: str = "", description: str = "") -> List[str]:
        """Extract and generate intelligent tags from page content."""
        tags = []
        
        # Extract existing HTML tags
        tag_selectors = [
            'meta[name="keywords"]',
            '.tags a',
            '.tag',
            '[rel="tag"]'
        ]
        
        for selector in tag_selectors:
            elements = soup.select(selector)
            for element in elements:
                if element.name == 'meta':
                    content = element.get('content', '')
                    if content:
                        tags.extend([tag.strip() for tag in content.split(',')])
                else:
                    tag_text = element.get_text(strip=True)
                    if tag_text:
                        tags.append(tag_text)
        
        # Add intelligent content-based tags
        content_text = (title + " " + description).lower()
        
        # Business and startup categories
        if any(word in content_text for word in ['startup', 'funding', 'venture', 'vc', 'investment', 'fundraising', 'seed', 'series a', 'series b']):
            tags.append('startup_funding')
            
        if any(word in content_text for word in ['business model', 'monetization', 'revenue', 'profit', 'subscription', 'saas']):
            tags.append('business_models')
            
        # Creator economy
        if any(word in content_text for word in ['creator', 'influencer', 'content creator', 'youtube', 'tiktok', 'instagram', 'patreon']):
            tags.append('creator_economy')
            
        if any(word in content_text for word in ['monetization', 'sponsorship', 'brand partnership', 'affiliate marketing']):
            tags.append('creator_monetization')
            
        # Technology
        if any(word in content_text for word in ['ai', 'artificial intelligence', 'machine learning', 'deep learning', 'gpt', 'llm']):
            tags.append('ai_technology')
            
        if any(word in content_text for word in ['crypto', 'bitcoin', 'ethereum', 'blockchain', 'web3', 'defi', 'nft']):
            tags.append('crypto_web3')
            
        # Media industry
        if any(word in content_text for word in ['media', 'journalism', 'publishing', 'news', 'content', 'streaming', 'podcast']):
            tags.append('media_industry')
            
        if any(word in content_text for word in ['subscription', 'paywall', 'digital media', 'newsletter']):
            tags.append('media_business_models')
            
        # Market trends
        if any(word in content_text for word in ['trend', 'market', 'analysis', 'forecast', 'prediction', 'outlook']):
            tags.append('market_trends')
            
        # Finance and economics
        if any(word in content_text for word in ['stock', 'market', 'trading', 'finance', 'economy', 'inflation', 'recession']):
            tags.append('finance_economics')
            
        return list(set(tags))  # Remove duplicates
    
    def _extract_published_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extract published date from page."""
        from dateutil import parser
        
        # Try various date selectors
        date_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="publish_date"]',
            'meta[name="date"]',
            '.published',
            '.date',
            'time'
        ]
        
        for selector in date_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    date_str = element.get('content')
                elif element.name == 'time':
                    date_str = element.get('datetime') or element.get_text(strip=True)
                else:
                    date_str = element.get_text(strip=True)
                
                if date_str:
                    try:
                        return parser.parse(date_str)
                    except:
                        continue
        
        return None
    
    @abstractmethod
    def scrape_content(self, source_url: str) -> List[Content]:
        """Scrape content from a source URL. Must be implemented by subclasses."""
        pass
    
    def cleanup(self):
        """Clean up resources."""
        if self.driver:
            self.driver.quit()
            self.driver = None
        if self.session:
            self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
