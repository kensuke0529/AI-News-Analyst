#!/usr/bin/env python3
"""
Railway Debug Script
===================
This script helps debug Railway deployment issues.
"""
import requests
import json
import sys

def test_railway_deployment(base_url):
    """Test Railway deployment step by step"""
    print("🔍 RAILWAY DEPLOYMENT DEBUG")
    print("=" * 50)
    print(f"Testing: {base_url}")
    print()
    
    # Step 1: Test basic connectivity
    print("1️⃣ Testing basic connectivity...")
    try:
        response = requests.get(f"{base_url}/api/status", timeout=10)
        if response.status_code == 200:
            print("✅ Site is accessible")
            data = response.json()
            print(f"   Daily limit: {data.get('daily_limit')}")
            print(f"   Used today: {data.get('used_today')}")
        else:
            print(f"❌ Site returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot reach site: {e}")
        return False
    
    # Step 2: Test RAG endpoint
    print("\n2️⃣ Testing RAG endpoint...")
    try:
        response = requests.post(
            f"{base_url}/api/news/rag",
            json={"query": "test query"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '')
            
            if "I apologize, but I couldn't retrieve any relevant information" in response_text:
                print("❌ Still showing old error - database is empty or old code")
                print("   This means either:")
                print("   - Railway hasn't redeployed yet")
                print("   - Database is empty")
                print("   - Old code is still running")
                return False
            else:
                print("✅ RAG is working with new code")
                return True
        else:
            print(f"❌ RAG failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ RAG test failed: {e}")
        return False

def populate_railway_database(base_url):
    """Try to populate Railway database"""
    print("\n3️⃣ Attempting to populate Railway database...")
    try:
        response = requests.post(
            f"{base_url}/api/admin/update-news",
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Database population successful!")
            print(f"   Status: {data.get('status')}")
            print(f"   New articles: {data.get('new_articles')}")
            print(f"   Total articles: {data.get('total_articles')}")
            return True
        else:
            print(f"❌ Database population failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Database population error: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python debug_railway.py <your-railway-url>")
        print("Example: python debug_railway.py https://ai-news-analyst-production.up.railway.app")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    # Test the deployment
    if test_railway_deployment(base_url):
        print("\n🎉 SUCCESS! Your Railway deployment is working correctly!")
    else:
        print("\n🔧 Trying to fix the issue...")
        
        # Try to populate the database
        if populate_railway_database(base_url):
            print("\n🔄 Database populated. Testing RAG again...")
            
            # Test RAG again
            try:
                response = requests.post(
                    f"{base_url}/api/news/rag",
                    json={"query": "what is the latest news?"},
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    response_text = data.get('response', '')
                    
                    if "I apologize, but I couldn't retrieve any relevant information" in response_text:
                        print("❌ Still not working after database population")
                        print("   This suggests the old code is still running")
                        print("   Check Railway dashboard for deployment status")
                    else:
                        print("✅ FIXED! RAG is now working correctly!")
                        print(f"   Response: {response_text[:200]}...")
                else:
                    print(f"❌ RAG still failing: {response.status_code}")
            except Exception as e:
                print(f"❌ RAG test failed: {e}")
        else:
            print("\n❌ Could not populate database")
            print("   Possible issues:")
            print("   - Railway environment variables not set")
            print("   - ChromaDB Cloud connection issues")
            print("   - API keys missing or incorrect")

if __name__ == "__main__":
    main()
