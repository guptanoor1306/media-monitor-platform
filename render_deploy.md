# 🎨 Render Deployment (FREE OPTION)

## Why Render is Great:
- ✅ FREE tier available
- ✅ Native Python support
- ✅ Built-in PostgreSQL
- ✅ Background workers supported
- ✅ Simple deployment

## 🚀 Deploy Steps:

### 1. Create render.yaml
```yaml
databases:
  - name: media-monitor-db
    databaseName: media_monitor
    user: media_user

services:
  - type: web
    name: media-monitor-api
    env: python
    plan: free
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn src.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: media-monitor-db
          property: connectionString
      - key: OPENAI_API_KEY
        value: sk-your-openai-key
```

### 2. Connect GitHub & Deploy
1. Push code to GitHub
2. Connect repository to Render
3. Auto-deploy on every push!

## 🌐 Result:
- Live URL: `https://your-app.onrender.com`
- Free PostgreSQL database
- Automatic deployments
