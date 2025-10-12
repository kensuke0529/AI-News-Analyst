#!/usr/bin/env python3
"""
Test script to verify health check works locally
"""
import subprocess
import time
import sys
import os

def test_health_check():
    """Test the health check script"""
    print("Testing health check script...")
    
    # Set a test port
    os.environ["PORT"] = "8003"
    
    try:
        # Run the health check script
        result = subprocess.run([sys.executable, "scripts/health_check.py"], 
                              capture_output=True, text=True, timeout=15)
        
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")
        
        if result.returncode == 0:
            print("✅ Health check test passed!")
            return True
        else:
            print("❌ Health check test failed!")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Health check test timed out!")
        return False
    except Exception as e:
        print(f"❌ Health check test error: {e}")
        return False

if __name__ == "__main__":
    success = test_health_check()
    sys.exit(0 if success else 1)
