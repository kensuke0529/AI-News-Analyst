#!/usr/bin/env python3
"""
Production startup script for Railway deployment
Includes logging and environment validation
"""
import os
import sys
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def validate_environment():
    """Validate required environment variables"""
    required_vars = ['OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    # Check ChromaDB Cloud configuration if enabled
    if os.environ.get("USE_CHROMA_CLOUD", "false").lower() == "true":
        chroma_vars = ['CHROMA_API_KEY', 'CHROMA_TENANT']
        for var in chroma_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        return False
    
    logger.info("Environment validation passed")
    return True

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
                logger.info(f"✅ Database populated with {result['new_articles']} articles")
            else:
                logger.warning(f"⚠️  Database population had issues: {result.get('error', 'Unknown error')}")
        else:
            logger.info(f"✅ Database already has {len(existing_links)} articles")
            
    except Exception as e:
        logger.warning(f"⚠️  Could not check/populate database: {e}")
        logger.warning("App will start but may not have data available")

def main():
    """Main startup function"""
    logger.info("Starting AI News Analyst in production mode")
    logger.info(f"Startup time: {datetime.now().isoformat()}")
    
    # Log environment info
    port = os.environ.get("PORT", "8002")
    logger.info(f"Port: {port}")
    logger.info(f"Python version: {sys.version}")
    
    # Validate environment
    if not validate_environment():
        logger.error("Environment validation failed")
        sys.exit(1)
    
    # Skip database population on startup to avoid health check timeout
    # Database will be populated on first API call
    logger.info("Skipping database population on startup for faster health checks")
    
    # Import and run the backend
    try:
        import uvicorn
        from backend.main import app
        
        logger.info("Starting FastAPI server...")
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=int(port),
            reload=False,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()