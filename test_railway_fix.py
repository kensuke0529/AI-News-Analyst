#!/usr/bin/env python3
"""
Test Railway Fix
================
This script helps test if the Railway deployment is working correctly.
"""
import requests
import json
import sys

def test_railway_site(base_url):
    """Test the Railway site"""
    print(f"Testing Railway site: {base_url}")
    print("=" * 60)
    
    # Test 1: Check if site is up
    print("\n1. Testing site availability...")
    try:
        response = requests.get(f"{base_url}/api/status", timeout=10)
        if response.status_code == 200:
            print("✅ Site is up and running")
            data = response.json()
            print(f"   Daily limit: {data.get('daily_limit', 'Unknown')}")
            print(f"   Used today: {data.get('used_today', 'Unknown')}")
            print(f"   Remaining: {data.get('remaining_today', 'Unknown')}")
        else:
            print(f"❌ Site returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Site is not accessible: {e}")
        return False
    
    # Test 2: Test RAG endpoint
    print("\n2. Testing RAG endpoint...")
    try:
        response = requests.post(
            f"{base_url}/api/news/rag",
            json={"query": "what is the elon related news?"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '')
            
            print("✅ RAG endpoint is working")
            print(f"   Response length: {len(response_text)} characters")
            
            # Check if it's the old error message
            if "I apologize, but I couldn't retrieve any relevant information" in response_text:
                print("❌ Still showing old error message - database might be empty")
                print("   Try populating the database manually")
                return False
            else:
                print("✅ RAG is returning proper responses")
                print(f"   Response preview: {response_text[:200]}...")
                return True
        else:
            print(f"❌ RAG endpoint failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ RAG test failed: {e}")
        return False

def populate_database(base_url):
    """Try to populate the database"""
    print("\n3. Attempting to populate database...")
    try:
        response = requests.post(
            f"{base_url}/api/admin/update-news",
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Database population successful")
            print(f"   Status: {data.get('status', 'Unknown')}")
            print(f"   New articles: {data.get('new_articles', 'Unknown')}")
            print(f"   Total articles: {data.get('total_articles', 'Unknown')}")
            return True
        else:
            print(f"❌ Database population failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Database population failed: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_railway_fix.py <your-railway-url>")
        print("Example: python test_railway_fix.py https://ai-news-analyst-production.up.railway.app")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    print("RAILWAY DEPLOYMENT TEST")
    print("=" * 60)
    
    # Test the site
    if test_railway_site(base_url):
        print("\n✅ All tests passed! Your Railway deployment is working correctly.")
    else:
        print("\n❌ Tests failed. Trying to fix...")
        
        # Try to populate the database
        if populate_database(base_url):
            print("\n🔄 Database populated. Testing again...")
            if test_railway_site(base_url):
                print("\n✅ Fixed! Railway deployment is now working correctly.")
            else:
                print("\n❌ Still not working. Check Railway logs for errors.")
        else:
            print("\n❌ Could not populate database. Check Railway configuration.")

if __name__ == "__main__":
    main()
