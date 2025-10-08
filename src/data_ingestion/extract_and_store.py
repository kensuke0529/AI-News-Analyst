"""
Background Extraction Job
=========================
Fetch news from multiple sources and store in vector DB.
This runs independently from user queries.

Run this script periodically (cron, scheduler, etc.) to keep the DB updated.
"""
from src.data_sources.techmeme_rss_parser import get_text as get_techmeme_text
from src.data_sources.mit import get_text as get_mit_text
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain.schema import Document
import os
from datetime import datetime
from dotenv import load_dotenv
import warnings
import urllib3

# Suppress SSL warnings
warnings.filterwarnings('ignore', category=urllib3.exceptions.NotOpenSSLWarning)
os.environ['PYTHONWARNINGS'] = 'ignore::urllib3.exceptions.NotOpenSSLWarning'

load_dotenv()

def extract_and_store(persist_directory="./data/vector_db"):
    """
    Extract news from all sources and store in vector DB.
    This is a standalone job - no user query involved.
    
    Returns:
        dict: Statistics about the extraction job
    """
    print(f"\n{'='*60}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting Extraction Job")
    print(f"{'='*60}\n")
    
    # Initialize embedding model
    embedding_model = OpenAIEmbeddings(
        api_key=os.environ["OPENAI_API_KEY"], 
        model="text-embedding-3-small"
    )
    
    # 1. Fetch from all sources
    print("📡 Fetching articles from sources...")
    try:
        techmeme_articles = get_techmeme_text()
        print(f"  ✓ Techmeme: {len(techmeme_articles)} articles")
    except Exception as e:
        print(f"  ✗ Techmeme failed: {e}")
        techmeme_articles = []
    
    try:
        mit_articles = get_mit_text()
        print(f"  ✓ MIT: {len(mit_articles)} articles")
    except Exception as e:
        print(f"  ✗ MIT failed: {e}")
        mit_articles = []
    
    all_articles = techmeme_articles + mit_articles
    print(f"\n📊 Total fetched: {len(all_articles)} articles")
    
    if not all_articles:
        print("⚠️  No articles fetched. Exiting.")
        return {"new_articles": 0, "new_chunks": 0, "total_articles": 0}
    
    # 2. Load existing vector store
    print("\n💾 Loading existing vector store...")
    try:
        vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding_model
        )
        
        # Get existing article links to avoid duplicates
        existing_links = set()
        try:
            all_docs = vector_store.get()
            if all_docs and 'metadatas' in all_docs:
                existing_links = {doc['link'] for doc in all_docs['metadatas'] if 'link' in doc}
            print(f"  ✓ Found {len(existing_links)} existing articles in DB")
        except:
            existing_links = set()
            print(f"  ✓ Empty vector store")
    except:
        vector_store = None
        existing_links = set()
        print(f"  ✓ Creating new vector store")
    
    # 3. Filter new articles
    new_articles = [article for article in all_articles if article['link'] not in existing_links]
    
    if not new_articles:
        print("\n✨ No new articles to add. Database is up to date.")
        return {
            "new_articles": 0,
            "new_chunks": 0,
            "total_articles": len(existing_links),
            "status": "up_to_date"
        }
    
    print(f"\n🆕 Found {len(new_articles)} new articles to process")
    
    # Show breakdown by source
    sources_count = {}
    for article in new_articles:
        source = article.get('source', 'unknown')
        sources_count[source] = sources_count.get(source, 0) + 1
    print(f"   By source: {sources_count}")
    
    # 4. Chunk and create documents
    print("\n✂️  Chunking articles...")
    splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", ""],
        chunk_size=500,
        chunk_overlap=10
    )
    
    all_docs = []
    for article in new_articles:
        news_content = f"Title: {article['title']}, Content: {article['description']}"
        chunks = splitter.split_text(news_content)
        
        doc_objs = [
            Document(
                page_content=chunk,
                metadata={
                    "title": article["title"],
                    "link": article["link"],
                    "pub_date": article["pub_date"],
                    "source": article["source"],
                    "ingested_at": datetime.now().isoformat()
                }
            )
            for chunk in chunks
        ]
        all_docs.extend(doc_objs)
    
    print(f"  ✓ Created {len(all_docs)} chunks from {len(new_articles)} articles")
    
    # 5. Embed and store in vector DB
    print("\n🔮 Embedding and storing in vector DB...")
    try:
        if vector_store is None:
            vector_store = Chroma.from_documents(
                documents=all_docs,
                embedding=embedding_model,
                persist_directory=persist_directory
            )
        else:
            vector_store.add_documents(all_docs)
        
        print(f"  ✓ Successfully stored {len(all_docs)} chunks")
    except Exception as e:
        print(f"  ✗ Storage failed: {e}")
        return {
            "new_articles": len(new_articles),
            "new_chunks": 0,
            "total_articles": len(existing_links),
            "status": "failed",
            "error": str(e)
        }
    
    # 6. Summary
    total_articles = len(existing_links) + len(new_articles)
    result = {
        "new_articles": len(new_articles),
        "new_chunks": len(all_docs),
        "total_articles": total_articles,
        "sources": sources_count,
        "status": "success",
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"\n{'='*60}")
    print(f"✅ Extraction Complete!")
    print(f"{'='*60}")
    print(f"   New articles added: {result['new_articles']}")
    print(f"   New chunks created: {result['new_chunks']}")
    print(f"   Total articles in DB: {result['total_articles']}")
    print(f"{'='*60}\n")
    
    return result


if __name__ == "__main__":
    result = extract_and_store()
    print(f"\nFinal result: {result}")

