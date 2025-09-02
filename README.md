# 🚀 Media Monitor Platform

An AI-powered content aggregation and analysis platform that helps you stay updated with the latest trends in media, creator economy, and business models.

## ✨ Features

- **🧠 AI-Powered Analysis**: GPT-4 powered content summarization and insights
- **📡 Multi-Source Aggregation**: RSS feeds, blogs, podcasts, and news sources
- **🎛️ Smart Filtering**: Filter by source, category, and content type
- **💾 Persistent Storage**: SQLite (local) / PostgreSQL (cloud) support
- **🔒 Paywall Detection**: Smart identification of restricted content
- **📱 Modern UI**: Clean, magazine-style interface
- **🔄 Daily Refresh**: Automated content scraping and updates

## 🏗️ Built With

- **Backend**: FastAPI, SQLAlchemy, OpenAI API
- **Frontend**: HTML, JavaScript, Tailwind CSS
- **Database**: SQLite (development) / PostgreSQL (production)
- **AI**: OpenAI GPT-4 for content analysis
- **Deployment**: Ready for Render, Railway, or Vercel

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd media-monitor
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

5. **Run the application**
   ```bash
   python -m src.main
   ```

6. **Access the platform**
   ```
   http://localhost:8000
   ```

## 🌐 Deployment

### Render (Recommended - FREE)

1. Push to GitHub
2. Connect to Render.com
3. Add environment variable: `OPENAI_API_KEY`
4. Deploy! 🚀

See `RENDER_SIMPLE.md` for detailed instructions.

### Railway ($5/month)

```bash
./deploy.sh
```

See `railway_deploy.md` for details.

## 📁 Project Structure

```
├── src/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── models.py            # Database models
│   ├── database.py          # Database setup
│   └── services/            # Business logic
├── templates/               # HTML templates
├── static/                  # Static assets
├── scripts/                 # Utility scripts
└── deployment files         # Various deployment configs
```

## 🎯 Usage

1. **Browse Content**: Explore articles by category (Media, Creator Economy, etc.)
2. **Filter Sources**: Use source pills to filter by specific publications
3. **AI Analysis**: Select articles and generate custom AI summaries
4. **Daily Updates**: Click "Daily Refresh" to fetch latest content

## 🔑 Environment Variables

```env
OPENAI_API_KEY=sk-your-openai-api-key
DATABASE_URL=sqlite:///./media_monitor.db  # or PostgreSQL URL for production
```

## 📊 Features in Detail

### Content Sources
- Technology blogs and news sites
- Creator economy publications  
- Business and startup media
- Podcast RSS feeds
- VC firm blogs and reports

### AI Analysis
- Custom prompt analysis
- Business model insights
- Creator economy trends
- Media industry analysis

### Smart Filtering
- Source-based filtering
- Category organization
- Paywall content detection
- Date-based sorting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🛠️ Support

For issues and questions, please create a GitHub issue or contact the maintainer.

---

**Built with ❤️ for the media and creator economy community**