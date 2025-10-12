#!/usr/bin/env python3
"""
Health check script for AI News Analyst
Checks if all services are running and responding correctly
"""

import requests
import json
import sys
from datetime import datetime

def check_service(url, name, timeout=10):
    """Check if a service is responding"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"✅ {name}: OK")
            return True
        else:
            print(f"❌ {name}: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {name}: {e}")
        return False

def check_api_status():
    """Check API status endpoint"""
    try:
        response = requests.get("http://localhost:8002/api/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            print(f"📊 Token Usage: {status['used_today']}/{status['daily_limit']} ({status['percentage_used']}%)")
            print(f"🔄 Status: {status['status']}")
            return True
        else:
            print(f"❌ API Status: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API Status: {e}")
        return False

def main():
    """Main health check function"""
    print("🏥 AI News Analyst Health Check")
    print("=" * 40)
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check services
    backend_ok = check_service("http://localhost:8002/", "Backend API")
    frontend_ok = check_service("http://localhost:3000/", "Frontend")
    
    print()
    
    # Check API status
    if backend_ok:
        check_api_status()
    
    print()
    
    # Summary
    if backend_ok and frontend_ok:
        print("🎉 All services are healthy!")
        sys.exit(0)
    else:
        print("⚠️  Some services are not responding")
        sys.exit(1)

if __name__ == "__main__":
    main()
