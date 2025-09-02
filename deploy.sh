#!/bin/bash

# 🚀 Quick Deploy Script for Railway

echo "🚂 Deploying Media Monitor to Railway..."
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "📦 Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Login to Railway
echo "🔐 Please login to Railway..."
railway login

# Create new project
echo "🆕 Creating new Railway project..."
railway new

# Add PostgreSQL database
echo "🗄️ Adding PostgreSQL database..."
railway add --database postgresql

# Deploy the application
echo "🚀 Deploying your application..."
railway deploy

echo ""
echo "✅ Deployment Complete!"
echo ""
echo "🔧 Next Steps:"
echo "1. Go to your Railway dashboard"
echo "2. Add environment variable: OPENAI_API_KEY"
echo "3. Your app will be live at: https://your-app.railway.app"
echo ""
echo "🎉 Your Media Monitor Platform is now hosted on Railway!"
