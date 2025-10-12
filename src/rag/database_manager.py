"""
Database manager for handling both local and cloud ChromaDB instances
"""
import os
from typing import Optional, Dict, Any, List
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from src.utils.config import (
    USE_CHROMA_CLOUD, 
    CHROMA_API_KEY, 
    CHROMA_TENANT, 
    CHROMA_DATABASE,
    VECTOR_DB_PATH
)

class DatabaseManager:
    """Manages ChromaDB connections for both local and cloud instances"""
    
    def __init__(self):
        self.embedding_model = OpenAIEmbeddings(
            api_key=os.environ["OPENAI_API_KEY"], 
            model="text-embedding-3-small"
        )
        self._client = None
        self._collection = None
    
    def get_client(self):
        """Get ChromaDB client (cloud or local)"""
        if USE_CHROMA_CLOUD:
            if not self._client:
                import chromadb
                self._client = chromadb.CloudClient(
                    api_key=CHROMA_API_KEY,
                    tenant=CHROMA_TENANT,
                    database=CHROMA_DATABASE
                )
            return self._client
        else:
            # For local development, we'll use the LangChain Chroma wrapper
            return None
    
    def get_vector_store(self, collection_name: str = "news_articles") -> Chroma:
        """Get vector store instance"""
        if USE_CHROMA_CLOUD:
            # Use cloud ChromaDB
            client = self.get_client()
            return Chroma(
                client=client,
                collection_name=collection_name,
                embedding_function=self.embedding_model
            )
        else:
            # Use local ChromaDB
            return Chroma(
                persist_directory=VECTOR_DB_PATH,
                collection_name=collection_name,
                embedding_function=self.embedding_model
            )
    
    def get_collection(self, collection_name: str = "news_articles"):
        """Get direct collection access for advanced operations"""
        if USE_CHROMA_CLOUD:
            client = self.get_client()
            return client.get_collection(collection_name)
        else:
            # For local, we don't need direct collection access
            return None
    
    def get_existing_links(self, collection_name: str = "news_articles") -> set:
        """Get existing article links to avoid duplicates"""
        try:
            vector_store = self.get_vector_store(collection_name)
            all_docs = vector_store.get()
            
            if all_docs and 'metadatas' in all_docs:
                existing_links = set()
                for metadata in all_docs['metadatas']:
                    if metadata and 'link' in metadata:
                        existing_links.add(metadata['link'])
                return existing_links
            return set()
        except Exception as e:
            print(f"Warning: Could not retrieve existing links: {e}")
            return set()
    
    def add_documents(self, documents: List[str], metadatas: List[Dict], 
                     collection_name: str = "news_articles") -> bool:
        """Add documents to the vector store"""
        try:
            vector_store = self.get_vector_store(collection_name)
            vector_store.add_texts(texts=documents, metadatas=metadatas)
            return True
        except Exception as e:
            print(f"Error adding documents: {e}")
            return False
    
    def search_documents(self, query: str, k: int = 3, 
                        collection_name: str = "news_articles") -> List[Dict]:
        """Search for similar documents"""
        try:
            vector_store = self.get_vector_store(collection_name)
            retriever = vector_store.as_retriever(
                search_type='similarity', 
                search_kwargs={"k": k}
            )
            docs = retriever.get_relevant_documents(query)
            
            # Format results
            results = []
            for doc in docs:
                results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata
                })
            return results
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def get_all_documents(self, collection_name: str = "news_articles") -> Dict[str, Any]:
        """Get all documents from the collection"""
        try:
            vector_store = self.get_vector_store(collection_name)
            return vector_store.get(include=['documents', 'metadatas'])
        except Exception as e:
            print(f"Error getting all documents: {e}")
            return {'documents': [], 'metadatas': []}

# Global instance
db_manager = DatabaseManager()
