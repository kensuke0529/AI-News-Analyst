#!/usr/bin/env python3
"""
Populate News Database Script
============================

This script fetches news articles from various sources and populates the vector database.
Run this script to update the news database with fresh articles.

Usage:
    python scripts/populate_news.py
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.data_ingestion.extract_and_store import extract_and_store

def main():
    """Main function to populate the news database"""
    print("Starting news database population...")
    print("=" * 60)
    
    try:
        result = extract_and_store()
        
        if result['status'] == 'success':
            print("\nSUCCESS: News database populated successfully!")
            print(f"   New articles added: {result['new_articles']}")
            print(f"   New chunks created: {result['new_chunks']}")
            print(f"   Total articles in DB: {result['total_articles']}")
            print(f"   Sources: {result['sources']}")
        elif result['status'] == 'up_to_date':
            print("\nDatabase is already up to date!")
            print(f"   Total articles in DB: {result['total_articles']}")
        else:
            print(f"\nFAILED: {result.get('error', 'Unknown error')}")
            return 1
            
    except Exception as e:
        print(f"\nERROR: Failed to populate database: {e}")
        return 1
    
    print("\nNews database population completed!")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

