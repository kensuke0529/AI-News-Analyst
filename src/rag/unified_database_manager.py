"""
Unified database manager that supports both ChromaDB and Supabase vector databases
"""
import os
from typing import Optional, Dict, Any, List
from src.utils.config import (
    USE_CHROMA_CLOUD, 
    USE_SUPABASE_VECTOR,
    VECTOR_DB_PATH
)
from src.rag.database_manager import DatabaseManager
from src.rag.supabase_manager import SupabaseVectorManager

class UnifiedDatabaseManager:
    """Unified manager that handles both ChromaDB and Supabase vector databases"""
    
    def __init__(self):
        self.chroma_manager = DatabaseManager()
        self.supabase_manager = SupabaseVectorManager()
        self._current_backend = None
    
    def _get_backend(self):
        """Determine which backend to use based on configuration"""
        if USE_SUPABASE_VECTOR:
            return "supabase"
        elif USE_CHROMA_CLOUD:
            return "chroma_cloud"
        else:
            return "chroma_local"
    
    def get_vector_store(self, collection_name: str = "news_articles"):
        """Get vector store instance based on current backend"""
        backend = self._get_backend()
        self._current_backend = backend
        
        if backend == "supabase":
            # For Supabase, we don't return a vector store object like ChromaDB
            # Instead, we return the manager itself
            return self.supabase_manager
        else:
            return self.chroma_manager.get_vector_store(collection_name)
    
    def get_existing_links(self, collection_name: str = "news_articles") -> set:
        """Get existing article links to avoid duplicates"""
        backend = self._get_backend()
        
        if backend == "supabase":
            return self.supabase_manager.get_existing_links(collection_name)
        else:
            return self.chroma_manager.get_existing_links(collection_name)
    
    def add_documents(self, documents: List[str], metadatas: List[Dict], 
                     collection_name: str = "news_articles") -> bool:
        """Add documents to the vector store"""
        backend = self._get_backend()
        
        if backend == "supabase":
            return self.supabase_manager.add_documents(documents, metadatas, collection_name)
        else:
            return self.chroma_manager.add_documents(documents, metadatas, collection_name)
    
    def search_documents(self, query: str, k: int = 3, 
                        collection_name: str = "news_articles") -> List[Dict]:
        """Search for similar documents"""
        backend = self._get_backend()
        
        if backend == "supabase":
            return self.supabase_manager.search_documents(query, k, collection_name)
        else:
            return self.chroma_manager.search_documents(query, k, collection_name)
    
    def get_all_documents(self, collection_name: str = "news_articles") -> Dict[str, Any]:
        """Get all documents from the collection"""
        backend = self._get_backend()
        
        if backend == "supabase":
            return self.supabase_manager.get_all_documents(collection_name)
        else:
            return self.chroma_manager.get_all_documents(collection_name)
    
    def initialize_database(self, collection_name: str = "news_articles") -> bool:
        """Initialize the database (create tables, collections, etc.)"""
        backend = self._get_backend()
        
        if backend == "supabase":
            return self.supabase_manager.create_vector_table(collection_name)
        else:
            # ChromaDB doesn't need explicit initialization
            return True
    
    def get_backend_info(self) -> Dict[str, Any]:
        """Get information about the current backend"""
        backend = self._get_backend()
        
        info = {
            "backend": backend,
            "status": "active"
        }
        
        if backend == "supabase":
            info.update({
                "type": "Supabase with pgvector",
                "url": os.getenv("SUPABASE_URL", "Not configured")
            })
        elif backend == "chroma_cloud":
            info.update({
                "type": "ChromaDB Cloud",
                "database": os.getenv("CHROMA_DATABASE", "Not configured")
            })
        else:
            info.update({
                "type": "ChromaDB Local",
                "path": VECTOR_DB_PATH
            })
        
        return info

# Global instance
unified_db_manager = UnifiedDatabaseManager()
