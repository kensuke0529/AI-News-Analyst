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
VECTOR_DB_PATH = "./data/vector_db"

# RAG Settings
CHUNK_SIZE = 100
CHUNK_OVERLAP = 10
RETRIEVAL_K = 3

# Embedding Model
EMBEDDING_MODEL = "text-embedding-3-small"
