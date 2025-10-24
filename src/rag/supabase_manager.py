"""
Supabase vector database manager for handling vector operations with pgvector
"""
import os
import json
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from src.utils.config import (
    SUPABASE_URL,
    SUPABASE_KEY,
    SUPABASE_SERVICE_KEY,
    USE_SUPABASE_VECTOR
)

class SupabaseVectorManager:
    """Manages Supabase vector database operations using pgvector"""
    
    def __init__(self):
        self.embedding_model = OpenAIEmbeddings(
            api_key=os.environ["OPENAI_API_KEY"], 
            model="text-embedding-3-small"
        )
        self._client: Optional[Client] = None
        self._service_client: Optional[Client] = None
    
    def get_client(self) -> Client:
        """Get Supabase client for regular operations"""
        if not self._client:
            self._client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return self._client
    
    def get_service_client(self) -> Client:
        """Get Supabase service client for admin operations"""
        if not self._service_client:
            self._service_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        return self._service_client
    
    def create_vector_table(self, table_name: str = "news_articles") -> bool:
        """Create vector table with pgvector support"""
        try:
            service_client = self.get_service_client()
            
            # Create table with vector column
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id BIGSERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                embedding VECTOR(1536), -- OpenAI text-embedding-3-small dimension
                metadata JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            -- Create index for vector similarity search
            CREATE INDEX IF NOT EXISTS {table_name}_embedding_idx 
            ON {table_name} USING ivfflat (embedding vector_cosine_ops);
            
            -- Create index for metadata queries
            CREATE INDEX IF NOT EXISTS {table_name}_metadata_idx 
            ON {table_name} USING GIN (metadata);
            """
            
            service_client.rpc('exec_sql', {'sql': create_table_sql}).execute()
            return True
        except Exception as e:
            print(f"Error creating vector table: {e}")
            return False
    
    def add_documents(self, documents: List[str], metadatas: List[Dict], 
                     table_name: str = "news_articles") -> bool:
        """Add documents with embeddings to Supabase"""
        try:
            client = self.get_client()
            
            # Generate embeddings
            embeddings = self.embedding_model.embed_documents(documents)
            
            # Prepare data for insertion
            records = []
            for i, (doc, metadata, embedding) in enumerate(zip(documents, metadatas, embeddings)):
                records.append({
                    'content': doc,
                    'embedding': embedding,
                    'metadata': metadata
                })
            
            # Insert into Supabase
            result = client.table(table_name).insert(records).execute()
            return len(result.data) > 0
            
        except Exception as e:
            print(f"Error adding documents to Supabase: {e}")
            return False
    
    def search_documents(self, query: str, k: int = 3, 
                        table_name: str = "news_articles") -> List[Dict]:
        """Search for similar documents using vector similarity"""
        try:
            client = self.get_client()
            
            # Generate query embedding
            query_embedding = self.embedding_model.embed_query(query)
            
            # Perform vector similarity search
            result = client.rpc(
                'search_articles',
                {
                    'query_embedding': query_embedding,
                    'match_threshold': 0.5,
                    'match_count': k
                }
            ).execute()
            
            # Format results
            results = []
            for row in result.data:
                results.append({
                    'content': row['content'],
                    'metadata': row['metadata'],
                    'similarity': row.get('similarity', 0)
                })
            
            return results
            
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def get_existing_links(self, table_name: str = "news_articles") -> set:
        """Get existing article links to avoid duplicates"""
        try:
            client = self.get_client()
            result = client.table(table_name).select('metadata').execute()
            
            existing_links = set()
            for row in result.data:
                if row['metadata'] and 'link' in row['metadata']:
                    existing_links.add(row['metadata']['link'])
            
            return existing_links
            
        except Exception as e:
            print(f"Warning: Could not retrieve existing links: {e}")
            return set()
    
    def get_all_documents(self, table_name: str = "news_articles") -> Dict[str, Any]:
        """Get all documents from the table"""
        try:
            client = self.get_client()
            result = client.table(table_name).select('content, metadata').execute()
            
            documents = []
            metadatas = []
            
            for row in result.data:
                documents.append(row['content'])
                metadatas.append(row['metadata'])
            
            return {
                'documents': documents,
                'metadatas': metadatas
            }
            
        except Exception as e:
            print(f"Error getting all documents: {e}")
            return {'documents': [], 'metadatas': []}
    
    def delete_document(self, document_id: int, table_name: str = "news_articles") -> bool:
        """Delete a document by ID"""
        try:
            client = self.get_client()
            result = client.table(table_name).delete().eq('id', document_id).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    def update_document(self, document_id: int, content: str, metadata: Dict, 
                       table_name: str = "news_articles") -> bool:
        """Update a document and regenerate its embedding"""
        try:
            client = self.get_client()
            
            # Generate new embedding
            embedding = self.embedding_model.embed_query(content)
            
            # Update document
            result = client.table(table_name).update({
                'content': content,
                'embedding': embedding,
                'metadata': metadata,
                'updated_at': 'now()'
            }).eq('id', document_id).execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            print(f"Error updating document: {e}")
            return False

# Global instance
supabase_manager = SupabaseVectorManager()
