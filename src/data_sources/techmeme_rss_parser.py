import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from bs4 import BeautifulSoup
import warnings
import urllib3
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document
import os
from dotenv import load_dotenv

# Suppress SSL warnings completely
try:
    warnings.filterwarnings('ignore', category=urllib3.exceptions.NotOpenSSLWarning)
    os.environ['PYTHONWARNINGS'] = 'ignore::urllib3.exceptions.NotOpenSSLWarning'
except AttributeError:
    # urllib3 version doesn't have NotOpenSSLWarning
    pass

techmeme_rss = "https://www.techmeme.com/feed.xml"

def parse_techmeme_rss():
    try:
        response = requests.get(techmeme_rss)
        root = ET.fromstring(response.content)
        
        articles = []
        for item in root.findall('.//item'):
            title = item.find('title').text if item.find('title') is not None else "No title"
            link = item.find('link').text if item.find('link') is not None else "No link"
            description = item.find('description').text if item.find('description') is not None else "No description"
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else "No date"
            
            articles.append({
                'title': title,
                'link': link,
                'description': description,
                'pub_date': pub_date,
                'source' : 'techmeme'
            })
        
        return articles
    
    except Exception as e:
        print(f"Error parsing RSS: {e}")
        return []

def get_text():
    articles = parse_techmeme_rss()
    for i in range(len(articles)):
        soup = BeautifulSoup(articles[i]['description'], "html.parser")
        text = soup.get_text()
        articles[i]['description'] = text
    return articles

# ========================
# Embedding
# ========================

load_dotenv()
openai_api_key = os.environ["OPENAI_API_KEY"]
embedding_model = OpenAIEmbeddings(api_key=openai_api_key, model="text-embedding-3-small")

def Embedding_news(persist_directory="./data/vector_db"):
    """
    Create or update vector store with new articles, avoiding duplicates.
    """

    print("=== Searching Related news ===")
    articles = get_text()
    splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", ""],
        chunk_size=500,
        chunk_overlap=10
    )

    # Try to load existing vector store
    try:
        vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding_model
        )
        # Get existing article links to avoid duplicates
        existing_links = set()
        try:
            # Get all documents to check existing links
            all_docs = vector_store.get()
            if all_docs and 'metadatas' in all_docs:
                existing_links = {doc['link'] for doc in all_docs['metadatas'] if 'link' in doc}
        except:
            # If we can't retrieve existing docs, start fresh
            existing_links = set()
    except:
        # If no existing store, create new one
        vector_store = None
        existing_links = set()

    # Filter out articles that already exist
    new_articles = [article for article in articles if article['link'] not in existing_links]
    
    if not new_articles:
        print("No new articles to add.")
        if vector_store is None:
            # Create empty vector store if none exists
            vector_store = Chroma(
                persist_directory=persist_directory,
                embedding_function=embedding_model
            )
        return vector_store

    print(f"Adding {len(new_articles)} new articles to vector store.")

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
                    "source": article["source"]
                }
            )
            for chunk in chunks
        ]

        all_docs.extend(doc_objs)

    if vector_store is None:
        # Create new vector store
        vector_store = Chroma.from_documents(
            documents=all_docs,
            embedding=embedding_model,
            persist_directory=persist_directory
        )
    else:
        # Add new documents to existing store
        vector_store.add_documents(all_docs)

    return vector_store

