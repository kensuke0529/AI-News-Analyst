#!/usr/bin/env python3
"""
Railway-optimized startup script
Based on Railway community recommendations for healthcheck issues
"""
import os
import sys
import logging

# Minimal logging setup
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def main():
    """Railway-optimized startup with proper PORT handling"""
    # Railway injects PORT environment variable - this is critical for healthchecks
    port = os.environ.get("PORT", "8000")  # Default to 8000 if not set
    
    logger.info(f"Starting on Railway port: {port}")
    logger.info("PORT variable is required for Railway healthchecks to work")
    
    try:
        import uvicorn
        from backend.main import app
        
        # Railway-specific configuration
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",  # Must bind to all interfaces for Railway
            port=int(port),  # Must use Railway's injected PORT
            reload=False,
            log_level="error",  # Minimal logging for faster startup
            access_log=False,
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
