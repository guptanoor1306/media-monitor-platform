#!/bin/bash
# Setup real-time scraping (every 15 minutes)

PROJECT_DIR="/Users/noorgupta/Downloads/fos"
PYTHON_PATH="$PROJECT_DIR/venv/bin/python"
SCRIPT_PATH="$PROJECT_DIR/scripts/realtime_scraper.py"

# Make script executable
chmod +x "$SCRIPT_PATH"

# Create logs directory
mkdir -p "$PROJECT_DIR/logs"

# Real-time cron job (every 15 minutes)
CRON_JOB="*/15 * * * * cd $PROJECT_DIR && $PYTHON_PATH $SCRIPT_PATH >> $PROJECT_DIR/logs/realtime_scrape.log 2>&1"

# Add to crontab (check if already exists first)
(crontab -l 2>/dev/null | grep -v "$SCRIPT_PATH"; echo "$CRON_JOB") | crontab -

echo "✅ Real-time scraping setup complete!"
echo "⏰ Updates every 15 minutes: $CRON_JOB"
echo "📝 Logs: $PROJECT_DIR/logs/realtime_scrape.log"
echo ""
echo "🔧 To test immediately:"
echo "  python $SCRIPT_PATH"
echo ""
echo "🔧 To view logs:"
echo "  tail -f $PROJECT_DIR/logs/realtime_scrape.log"
