#!/usr/bin/env python3
"""
Quick startup script for Railway deployment
Minimal initialization to pass health checks quickly
"""
import os
import sys
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Quick startup with minimal validation"""
    port = os.environ.get("PORT", "8002")
    logger.info(f"Starting server on port {port}")
    
    try:
        import uvicorn
        from backend.main import app
        
        logger.info("Starting FastAPI server with minimal configuration...")
        
        # Start with absolute minimal configuration
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=int(port),
            reload=False,
            log_level="warning",  # Reduce log verbosity
            access_log=False,
            server_header=False,
            date_header=False
        )
    except Exception as e:
        logger.error(f"Failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
