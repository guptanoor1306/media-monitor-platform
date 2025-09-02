# Media Monitor Platform - Setup Guide

This guide will walk you through setting up the Media Monitor platform on your local machine.

## Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- Redis (optional, for advanced features)
- Chrome/Chromium browser (for Selenium web scraping)

## Step 1: Clone and Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd fos
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Step 2: Database Setup

1. **Install PostgreSQL**
   - **macOS**: `brew install postgresql`
   - **Ubuntu/Debian**: `sudo apt-get install postgresql postgresql-contrib`
   - **Windows**: Download from [postgresql.org](https://www.postgresql.org/download/windows/)

2. **Create database and user**
   ```sql
   CREATE DATABASE media_monitor;
   CREATE USER mediamonitor WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE media_monitor TO mediamonitor;
   ```

3. **Update environment variables**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` file with your database credentials:
   ```env
   DATABASE_URL=postgresql://mediamonitor:your_password@localhost/media_monitor
   ```

## Step 3: API Keys Setup

### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account and get your API key
3. Add to `.env`:
   ```env
   OPENAI_API_KEY=sk-your-api-key-here
   ```

### Twitter API (Optional)
1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create an app and get your API keys
3. Add to `.env`:
   ```env
   TWITTER_API_KEY=your_twitter_api_key
   TWITTER_API_SECRET=your_twitter_api_secret
   TWITTER_ACCESS_TOKEN=your_twitter_access_token
   TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
   TWITTER_BEARER_TOKEN=your_twitter_bearer_token
   ```

### Reddit API (Optional)
1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Create a new app and get your client credentials
3. Add to `.env`:
   ```env
   REDDIT_CLIENT_ID=your_reddit_client_id
   REDDIT_CLIENT_SECRET=your_reddit_client_secret
   ```

### Spotify API (Optional)
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Create a new app and get your client credentials
3. Add to `.env`:
   ```env
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   ```

## Step 4: Initialize Database

1. **Run the database initialization script**
   ```bash
   python scripts/init_db.py
   ```

   This will:
   - Create all necessary database tables
   - Add sample media sources
   - Create a demo user

## Step 5: Start the Application

1. **Start the platform**
   ```bash
   python main.py
   ```

2. **Access the application**
   - **Dashboard**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/health

## Step 6: First Steps

1. **Browse the dashboard**
   - The platform comes with pre-loaded sample sources
   - You can see content from various media types

2. **Add your own sources**
   - Click "Add Source" button
   - Enter source details (URL, type, description)
   - The platform will auto-detect the appropriate scraper

3. **Test content scraping**
   - Click "Refresh" to fetch new content from sources
   - Monitor the console for scraping progress

4. **Try AI summarization**
   - Select multiple content items using checkboxes
   - Click "AI Summarize" button
   - Choose analysis type or enter custom prompt

## Configuration Options

### Update Intervals
Control how often sources are updated:
```env
DEFAULT_UPDATE_INTERVAL=3600  # 1 hour in seconds
```

### Content Limits
Manage content storage:
```env
MAX_CONTENT_LENGTH=10000      # Max characters per content item
SUMMARIZATION_MAX_TOKENS=1000 # Max tokens for AI summaries
```

### Scraping Settings
```env
SELENIUM_HEADLESS=true        # Run browser in background
REQUEST_TIMEOUT=30            # HTTP request timeout
MAX_RETRIES=3                # Retry failed requests
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify PostgreSQL is running
   - Check database credentials in `.env`
   - Ensure database exists

2. **Scraping Failures**
   - Check internet connection
   - Verify source URLs are accessible
   - Check console for specific error messages

3. **AI Summarization Errors**
   - Verify OpenAI API key is valid
   - Check API usage limits
   - Ensure content items are selected

4. **Selenium Issues**
   - Install Chrome/Chromium browser
   - Update ChromeDriver if needed
   - Check if `SELENIUM_HEADLESS=true` in `.env`

### Performance Optimization

1. **Database Indexing**
   ```sql
   CREATE INDEX idx_content_published_at ON contents(published_at);
   CREATE INDEX idx_content_source_id ON contents(source_id);
   ```

2. **Content Cleanup**
   - Run cleanup periodically: `POST /api/admin/cleanup`
   - Adjust `days_to_keep` parameter as needed

3. **Scraping Limits**
   - Set appropriate update intervals for different source types
   - Use rate limiting for social media APIs

## Advanced Features

### Scheduled Tasks
Create automated monitoring:
```bash
# Example: Weekly podcast summary
curl -X POST "http://localhost:8000/api/scheduled-tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Weekly Podcast Summary",
    "source_ids": [2, 6],
    "prompt": "Summarize key insights from this week\'s podcast episodes",
    "schedule": "0 9 * * 1"
  }'
```

### Custom Alerts
Monitor specific keywords:
```bash
curl -X POST "http://localhost:8000/api/alerts" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Media Business Models",
    "keywords": ["business model", "revenue", "monetization"]
  }'
```

### Content Filtering
Filter content by various criteria:
```bash
# Get content from specific source types
GET /api/content?source_type=podcast

# Search for specific content
GET /api/content/search?q=creator economy

# Get user-specific content
GET /api/users/1/content?source_types=blog,podcast
```

## Production Deployment

### Environment Variables
Set production values:
```env
DEBUG=false
LOG_LEVEL=WARNING
HOST=0.0.0.0
PORT=8000
```

### Process Management
Use a process manager like PM2 or systemd:
```bash
# PM2 example
pm2 start main.py --name "media-monitor" --interpreter python

# Systemd example
sudo systemctl enable media-monitor
sudo systemctl start media-monitor
```

### Reverse Proxy
Set up Nginx or Apache:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Support and Contributing

- **Issues**: Report bugs and feature requests
- **Documentation**: Improve setup guides and API docs
- **Code**: Submit pull requests for improvements
- **Testing**: Help test with different source types

## License

This project is licensed under the MIT License - see the LICENSE file for details.
