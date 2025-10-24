"""
Configuration settings for the AI News Analyst application.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0"))

# Data Sources
TECHMEME_RSS_URL = "https://www.techmeme.com/feed.xml"

# Vector Database
VECTOR_DB_PATH = "./data/vector_db"  # Fallback for local development
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
CHROMA_TENANT = os.getenv("CHROMA_TENANT")
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE", "news-ai")
USE_CHROMA_CLOUD = os.getenv("USE_CHROMA_CLOUD", "false").lower() == "true"

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # anon key
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # service role key
USE_SUPABASE_VECTOR = os.getenv("USE_SUPABASE_VECTOR", "false").lower() == "true"

# RAG Settings
CHUNK_SIZE = 100
CHUNK_OVERLAP = 10
RETRIEVAL_K = 3

# Embedding Model
EMBEDDING_MODEL = "text-embedding-3-small"
