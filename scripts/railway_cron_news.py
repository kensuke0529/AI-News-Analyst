#!/usr/bin/env python3
"""
Railway Cron Job for Daily News Extraction
==========================================
This script is designed to run as a Railway cron job to extract news daily.
It runs the extraction process and then exits cleanly.
"""

import sys
import os
import logging
from datetime import datetime

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Set up logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

def main():
    """Main function for Railway cron job"""
    logger.info("🚀 Starting Railway daily news extraction")
    logger.info(f"📅 Date: {datetime.now()}")
    logger.info(f"🌍 Environment: Railway")
    
    try:
        from src.data_ingestion.extract_and_store import extract_and_store
        
        # Run the extraction
        result = extract_and_store()
        
        if result.get('status') == 'success':
            logger.info("✅ Railway extraction completed successfully!")
            logger.info(f"   📰 New articles: {result.get('new_articles', 0)}")
            logger.info(f"   📄 New chunks: {result.get('new_chunks', 0)}")
            logger.info(f"   📊 Total articles: {result.get('total_articles', 0)}")
            logger.info(f"   📅 Sources: {result.get('sources', {})}")
        elif result.get('status') == 'up_to_date':
            logger.info("✨ Database is already up to date!")
            logger.info(f"   📊 Total articles: {result.get('total_articles', 0)}")
        else:
            logger.error(f"❌ Extraction failed: {result.get('error', 'Unknown error')}")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Railway extraction failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return 1
    
    logger.info("🏁 Railway daily extraction job finished")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
