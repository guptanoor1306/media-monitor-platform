#!/usr/bin/env python3
"""
Media Monitor Platform - Main Entry Point
"""

import uvicorn
from src.main import app
from src.config import settings

if __name__ == "__main__":
    print("🚀 Starting Media Monitor Platform...")
    print(f"📡 Server will be available at: http://{settings.host}:{settings.port}")
    print(f"🔧 Debug mode: {settings.debug}")
    print(f"📊 API documentation: http://{settings.host}:{settings.port}/docs")
    
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
