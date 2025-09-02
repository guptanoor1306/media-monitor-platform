import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database - supports both SQLite (local) and PostgreSQL (cloud)
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./media_monitor.db")
    redis_url: str = "redis://localhost:6379"
    
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-3.5-turbo"
    
    # Twitter
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    twitter_access_token: Optional[str] = None
    twitter_access_token_secret: Optional[str] = None
    twitter_bearer_token: Optional[str] = None
    
    # Reddit
    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None
    reddit_user_agent: str = "MediaMonitor/1.0"
    
    # Spotify
    spotify_client_id: Optional[str] = None
    spotify_client_secret: Optional[str] = None
    
    # Web Scraping
    selenium_headless: bool = True
    request_timeout: int = 30
    max_retries: int = 3
    
    # Content Processing
    max_content_length: int = 10000
    summarization_max_tokens: int = 1000
    thumbnail_size: str = "300x200"
    
    # Monitoring
    default_update_interval: int = 3600  # 1 hour
    alert_check_interval: int = 300  # 5 minutes
    max_sources_per_user: int = 100
    
    # Server
    host: str = "0.0.0.0"
    port: int = int(os.getenv("PORT", "8001"))
    debug: bool = False
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
