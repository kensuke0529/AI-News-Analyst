#!/usr/bin/env python3
"""
Script to populate the database with initial data for Railway deployment
This ensures the app has some data to work with on first startup
"""
import os
import sys
import logging
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_ingestion.extract_and_store import extract_and_store
from src.utils.config import USE_CHROMA_CLOUD

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main function to populate the database"""
    logger.info("Starting database population...")
    logger.info(f"Using ChromaDB Cloud: {USE_CHROMA_CLOUD}")
    
    try:
        # Run the extraction and storage process
        result = extract_and_store()
        
        if result['status'] == 'success':
            logger.info("Database population completed successfully!")
            logger.info(f"   New articles: {result['new_articles']}")
            logger.info(f"   New chunks: {result['new_chunks']}")
            logger.info(f"   Total articles: {result['total_articles']}")
        elif result['status'] == 'up_to_date':
            logger.info("Database is already up to date!")
            logger.info(f"   Total articles: {result['total_articles']}")
        else:
            logger.error(f"Database population failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Database population failed with exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
