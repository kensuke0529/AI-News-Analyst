#!/usr/bin/env python3
"""
Test script to verify the application starts and healthcheck works locally
"""
import subprocess
import time
import requests
import sys
import os

def test_local_startup():
    """Test if the app starts locally and healthcheck works"""
    print("Testing local startup...")
    
    # Set test environment
    os.environ["PORT"] = "8001"
    
    try:
        # Start the app in background
        process = subprocess.Popen([
            sys.executable, "scripts/railway_start.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for startup
        print("Waiting for app to start...")
        time.sleep(10)
        
        # Test healthcheck endpoint
        try:
            response = requests.get("http://localhost:8001/healthz", timeout=5)
            if response.status_code == 200:
                print("✅ Healthcheck endpoint works!")
                print(f"Response: {response.text}")
                return True
            else:
                print(f"❌ Healthcheck failed with status: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Could not reach healthcheck endpoint: {e}")
            return False
        finally:
            # Clean up
            process.terminate()
            process.wait()
            
    except Exception as e:
        print(f"❌ Startup test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_local_startup()
    sys.exit(0 if success else 1)
