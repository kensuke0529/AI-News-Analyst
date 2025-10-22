#!/usr/bin/env python3
"""
Railway-optimized startup script
Based on Railway community recommendations for healthcheck issues
"""
import os
import sys
import logging

# Add the project root to Python path so we can import backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Minimal logging setup
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def populate_database_if_needed():
    """Populate database with initial data if needed"""
    try:
        from src.rag.database_manager import db_manager
        
        # Check if database has any data
        existing_links = db_manager.get_existing_links()
        
        if len(existing_links) == 0:
            logger.info("Database is empty, populating with initial data...")
            from src.data_ingestion.extract_and_store import extract_and_store
            
            result = extract_and_store()
            if result['status'] == 'success':
                logger.info(f"[OK] Database populated with {result['new_articles']} articles")
            else:
                logger.warning(f"[WARNING] Database population had issues: {result.get('error', 'Unknown error')}")
        else:
            logger.info(f"[OK] Database already has {len(existing_links)} articles")
            
    except Exception as e:
        logger.warning(f"[WARNING] Could not check/populate database: {e}")
        logger.warning("App will start but may not have data available")

def main():
    """Railway-optimized startup with proper PORT handling"""
    # Railway injects PORT environment variable - this is critical for healthchecks
    port = os.environ.get("PORT", "8000")  
    
    logger.info(f"Starting on Railway port: {port}")
    logger.info("PORT variable is required for Railway healthchecks to work")
    
    # Populate database if needed (for ChromaDB Cloud)
    populate_database_if_needed()
    
    try:
        import uvicorn
        from backend.main import app
        
        # Railway-specific configuration
        # Based on Railway community solution: bind to both IPv4 and IPv6
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
            # Railway optimizations
            timeout_keep_alive=30,
            timeout_graceful_shutdown=30
        )
    except Exception as e:
        logger.error(f"Railway startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
