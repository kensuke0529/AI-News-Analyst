#!/usr/bin/env python3
"""
Simple health check script for Railway deployment
Alternative to curl for health checks
"""
import sys
import os
import requests
import time

def health_check():
    """Perform health check on the application"""
    port = os.environ.get("PORT", "8002")
    url = f"http://localhost:{port}/health"
    
    try:
        # Add timeout to prevent hanging
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("Health check passed")
            return 0
        else:
            print(f"Health check failed with status code: {response.status_code}")
            return 1
            
    except requests.exceptions.RequestException as e:
        print(f"Health check failed: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error during health check: {e}")
        return 1

if __name__ == "__main__":
    # Give the server a moment to start
    time.sleep(5)
    sys.exit(health_check())