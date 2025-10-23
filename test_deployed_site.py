#!/usr/bin/env python3
"""
Test the deployed Railway site
Usage: python3 test_deployed_site.py <your-railway-url>
Example: python3 test_deployed_site.py https://ai-news-analyst-production.up.railway.app
"""
import sys
import requests
import json

def test_rag_endpoint(base_url, query="what is the tiktok related news?"):
    """Test the RAG endpoint"""
    url = f"{base_url}/api/news/rag"
    
    print(f"\n{'='*60}")
    print(f"Testing: {url}")
    print(f"Query: {query}")
    print('='*60)
    
    try:
        response = requests.post(
            url,
            json={"query": query},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '')
            
            print(f"\n✅ SUCCESS")
            print(f"Response length: {len(response_text)} characters")
            print(f"\nResponse preview:")
            print("-" * 60)
            print(response_text[:500])
            if len(response_text) > 500:
                print("...")
            print("-" * 60)
            
            # Check if it's the old "no information" bug
            if "provided context does not contain" in response_text.lower():
                print("\n⚠️  WARNING: Still showing 'no information' - old code is running")
                print("   Make sure you pushed the changes and Railway redeployed")
                return False
            else:
                print("\n✅ Response looks good! Fix is deployed.")
                return True
        else:
            print(f"\n❌ FAILED")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"\n❌ TIMEOUT: Request took longer than 30 seconds")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 test_deployed_site.py <your-railway-url>")
        print("Example: python3 test_deployed_site.py https://ai-news-analyst-production.up.railway.app")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    print("\n" + "="*60)
    print("DEPLOYED SITE RAG TEST")
    print("="*60)
    
    # Test different queries
    queries = [
        "what is the tiktok related news?",
        "latest AI developments",
    ]
    
    results = []
    for query in queries:
        results.append(test_rag_endpoint(base_url, query))
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("\n✅ All tests passed! Your deployed site is working correctly.")
    else:
        print("\n❌ Some tests failed.")
        print("\nPossible reasons:")
        print("1. Changes not pushed to GitHub yet")
        print("2. Railway hasn't redeployed yet (check Railway dashboard)")
        print("3. Different environment variables in production")

if __name__ == "__main__":
    main()

