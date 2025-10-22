#!/usr/bin/env python3
"""
Daily News Extraction Script
============================
This script runs daily to extract and store news articles.
It's designed to be run by launchd on macOS.
"""

import sys
import os
import logging
from datetime import datetime

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Set up logging
log_dir = os.path.join(project_root, "storage", "logs")
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, f"daily_extraction_{datetime.now().strftime('%Y%m%d')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main function to run daily news extraction"""
    logger.info("🚀 Starting daily news extraction job")
    logger.info(f"📅 Date: {datetime.now()}")
    logger.info(f"📁 Project root: {project_root}")
    
    try:
        from src.data_ingestion.extract_and_store import extract_and_store
        
        result = extract_and_store()
        
        if result.get('status') == 'success':
            logger.info("✅ Daily extraction completed successfully!")
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
        logger.error(f"❌ Extraction failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return 1
    
    logger.info("🏁 Daily extraction job finished")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
