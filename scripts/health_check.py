#!/usr/bin/env python3
import sys
import os
import urllib.request
import urllib.error
import time
import json

def health_check():
    """Perform health check on the application"""
    port = os.environ.get("PORT", "8002")
    url = f"http://localhost:{port}/health/live"
    
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Railway-HealthCheck/1.0')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                # Try to parse JSON response
                try:
                    data = json.loads(response.read().decode('utf-8'))
                    print(f"Health check passed: {data.get('status', 'unknown')}")
                except:
                    print("Health check passed (non-JSON response)")
                return 0
            else:
                print(f"Health check failed with status code: {response.status}")
                return 1
                
    except urllib.error.URLError as e:
        print(f"Health check failed - URL error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error during health check: {e}")
        return 1

if __name__ == "__main__":
    # Give the server a moment to start
    time.sleep(2)
    sys.exit(health_check())