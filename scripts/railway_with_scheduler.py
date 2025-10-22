#!/usr/bin/env python3
"""
Railway startup script with background news scheduler
==================================================
This script starts both the web server and a background scheduler
for daily news extraction.
"""
import os
import sys
import logging
import threading
import time
from datetime import datetime, timedelta
import schedule

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_news_extraction():
    """Run the news extraction job"""
    logger.info("🚀 Starting scheduled news extraction")
    try:
        from src.data_ingestion.extract_and_store import extract_and_store
        
        result = extract_and_store()
        
        if result.get('status') == 'success':
            logger.info("✅ Scheduled extraction completed!")
            logger.info(f"   📰 New articles: {result.get('new_articles', 0)}")
            logger.info(f"   📄 New chunks: {result.get('new_chunks', 0)}")
        elif result.get('status') == 'up_to_date':
            logger.info("✨ Database is already up to date!")
        else:
            logger.error(f"❌ Scheduled extraction failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"❌ Scheduled extraction failed: {e}")

def scheduler_worker():
    """Background scheduler worker"""
    logger.info("🕐 Starting background scheduler")
    
    # Schedule news extraction daily at 6:00 AM UTC
    schedule.every().day.at("06:00").do(run_news_extraction)
    
    # Run once on startup (optional)
    # run_news_extraction()
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

def main():
    """Main function to start both web server and scheduler"""
    port = os.environ.get("PORT", "8000")
    
    logger.info(f"Starting Railway service with scheduler on port: {port}")
    
    # Start background scheduler in a separate thread
    scheduler_thread = threading.Thread(target=scheduler_worker, daemon=True)
    scheduler_thread.start()
    
    try:
        import uvicorn
        from backend.main import app
        
        # Start the web server
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=int(port),
            reload=False,
            log_level="info",
            access_log=True,
            server_header=False,
            date_header=False,
            loop="asyncio",
            workers=1,
            timeout_keep_alive=30,
            timeout_graceful_shutdown=30
        )
    except Exception as e:
        logger.error(f"Railway startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
