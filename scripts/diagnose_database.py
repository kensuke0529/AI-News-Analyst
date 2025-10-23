#!/usr/bin/env python3
"""
Database Diagnostic Script
==========================
This script helps diagnose database configuration and content issues.
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from src.rag.database_manager import db_manager
from src.utils.config import USE_CHROMA_CLOUD, VECTOR_DB_PATH, CHROMA_DATABASE

load_dotenv()

def main():
    print("=" * 60)
    print("DATABASE DIAGNOSTIC TOOL")
    print("=" * 60)
    
    # 1. Check configuration
    print("\n📋 CONFIGURATION:")
    print(f"   USE_CHROMA_CLOUD: {USE_CHROMA_CLOUD}")
    print(f"   VECTOR_DB_PATH: {VECTOR_DB_PATH}")
    print(f"   CHROMA_DATABASE: {CHROMA_DATABASE}")
    
    # 2. Check database contents
    print("\n💾 DATABASE CONTENTS:")
    try:
        all_docs = db_manager.get_all_documents()
        doc_count = len(all_docs.get('documents', []))
        print(f"   Total documents: {doc_count}")
        
        if doc_count == 0:
            print("\n⚠️  WARNING: Database is EMPTY!")
            print("   This explains why RAG queries return 'no information'")
            print("\n💡 SOLUTION: Run the populate script:")
            print("   python scripts/populate_database.py")
            return
        
        # 3. Check for TikTok articles
        print("\n🔍 SEARCHING FOR TIKTOK:")
        tiktok_count = 0
        if all_docs.get('documents'):
            for i, doc in enumerate(all_docs['documents']):
                if 'tiktok' in doc.lower():
                    tiktok_count += 1
                    if tiktok_count <= 2:  # Show first 2
                        metadata = all_docs['metadatas'][i] if all_docs.get('metadatas') else {}
                        print(f"\n   Found TikTok doc {tiktok_count}:")
                        print(f"   Title: {metadata.get('title', 'No title')[:80]}...")
                        print(f"   Source: {metadata.get('source', 'Unknown')}")
        
        print(f"\n   Total TikTok documents: {tiktok_count}")
        
        # 4. Test search
        print("\n🎯 TESTING VECTOR SEARCH:")
        results = db_manager.search_documents("TikTok", k=3)
        print(f"   Search returned {len(results)} results")
        
        for i, result in enumerate(results[:2]):
            title = result['metadata'].get('title', 'No title')
            print(f"\n   Result {i+1}: {title[:80]}...")
        
        if len(results) > 0:
            print("\n✅ Database is working correctly!")
            print("   If the web interface shows 'no information',")
            print("   the issue is with the deployed environment.")
            print("\n💡 SOLUTION:")
            print("   1. Check if Railway is using cloud ChromaDB")
            print("   2. Populate the cloud database using:")
            print("      python scripts/populate_database.py")
            print("   3. Or set USE_CHROMA_CLOUD=false in Railway environment")
        else:
            print("\n❌ Search returned no results!")
            print("   Database exists but search isn't working.")
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\n💡 SOLUTION:")
        print("   The database might not be initialized.")
        print("   Run: python scripts/populate_database.py")

if __name__ == "__main__":
    main()

