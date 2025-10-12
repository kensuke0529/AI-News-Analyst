#!/usr/bin/env python3
"""
Script to run the FastAPI backend server
"""
import uvicorn
from backend.main import app

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
