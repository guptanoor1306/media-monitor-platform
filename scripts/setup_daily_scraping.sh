#!/bin/bash
# Setup daily scraping cron job

PROJECT_DIR="/Users/noorgupta/Downloads/fos"
PYTHON_PATH="$PROJECT_DIR/venv/bin/python"
SCRIPT_PATH="$PROJECT_DIR/scripts/daily_scrape.py"

# Create the daily scrape script
cat > "$SCRIPT_PATH" << 'EOF'
#!/usr/bin/env python3
"""
Daily scraping script to be run by cron
"""

import sys
import os
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.scraper_service import run_daily_scrape

def main():
    """Main function for daily scraping"""
    try:
        print(f"🚀 Starting daily scrape at {datetime.now()}")
        results = asyncio.run(run_daily_scrape())
        total_items = sum(results.values())
        print(f"✅ Daily scrape completed: {total_items} items added")
        return 0
    except Exception as e:
        print(f"❌ Daily scrape failed: {str(e)}")
        return 1

if __name__ == "__main__":
    from datetime import datetime
    exit(main())
EOF

# Make script executable
chmod +x "$SCRIPT_PATH"

# Add cron job (runs daily at 6 AM)
CRON_JOB="0 6 * * * cd $PROJECT_DIR && $PYTHON_PATH $SCRIPT_PATH >> $PROJECT_DIR/logs/daily_scrape.log 2>&1"

# Create logs directory
mkdir -p "$PROJECT_DIR/logs"

# Add to crontab (check if already exists first)
(crontab -l 2>/dev/null | grep -v "$SCRIPT_PATH"; echo "$CRON_JOB") | crontab -

echo "✅ Daily scraping setup complete!"
echo "📅 Cron job: $CRON_JOB"
echo "📝 Logs will be written to: $PROJECT_DIR/logs/daily_scrape.log"
echo ""
echo "🔧 To manage the cron job:"
echo "  View: crontab -l"
echo "  Edit: crontab -e"
echo "  Remove: crontab -r"
