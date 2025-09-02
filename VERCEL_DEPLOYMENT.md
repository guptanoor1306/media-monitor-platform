# Vercel Deployment Guide

## ⚠️ IMPORTANT: Required Changes for Vercel

### 1. Database Migration (REQUIRED)
- Replace SQLite with PostgreSQL (Vercel compatible)
- Use services like:
  - **Neon** (free PostgreSQL): https://neon.tech
  - **Supabase** (free tier): https://supabase.com
  - **Railway** (PostgreSQL): https://railway.app

### 2. Update Database Configuration

```python
# src/config.py - Replace SQLite URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@host:5432/dbname")
```

### 3. Environment Variables in Vercel

```bash
# Add these in Vercel dashboard
DATABASE_URL=postgresql://your-connection-string
OPENAI_API_KEY=sk-your-openai-key
```

### 4. Modify main.py for Serverless

```python
# src/main.py - Add at the top
import os
from mangum import Mangum

# At the bottom - Add handler for Vercel
handler = Mangum(app)
```

### 5. Install Additional Dependencies

```bash
pip install mangum psycopg2-binary
```

## 🚀 Deployment Steps

1. **Setup Database**:
   ```bash
   # Create PostgreSQL database on Neon/Supabase
   # Get connection string
   ```

2. **Update Code**:
   ```bash
   # Replace SQLite with PostgreSQL
   # Add mangum handler
   # Update requirements.txt
   ```

3. **Deploy to Vercel**:
   ```bash
   npm install -g vercel
   vercel login
   vercel --prod
   ```

4. **Set Environment Variables**:
   - Go to Vercel dashboard
   - Add DATABASE_URL and OPENAI_API_KEY

## ❌ Limitations on Vercel

- No background scraping tasks
- 10-30 second function timeout
- Cold starts may affect performance
- No persistent file system
- Complex setup for full-stack Python apps

## ✅ Better Alternatives

Consider these platforms for easier deployment:
- **Railway**: Best for Python apps with databases
- **Render**: Great free tier, supports background tasks  
- **DigitalOcean App Platform**: Full container support
- **Fly.io**: Fast global deployment
