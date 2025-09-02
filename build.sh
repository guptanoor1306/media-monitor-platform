#!/bin/bash
set -e

echo "🐍 Forcing Python 3.11 environment..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Build completed successfully!"
