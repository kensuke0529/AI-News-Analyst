from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.workflow.news_analysis_workflow import run_news_analysis
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class NewsQuery(BaseModel):
    query: str

@app.get("/")
def root():
    return {"message": "AI News Analyst API is running"}

@app.post("/api/news/rag")
def rag_news(news_query: NewsQuery):
    prompt = news_query.query
    result = run_news_analysis(prompt)
    return {"response": result}

@app.get('/api/news/all')
def get_news():
    try:
        embedding_model = OpenAIEmbeddings(
            api_key=os.environ["OPENAI_API_KEY"], 
            model="text-embedding-3-small"
        )
        
        vector_store = Chroma(
            persist_directory="./data/vector_db",
            embedding_function=embedding_model
        )
        
        # Get all documents
        all_docs = vector_store.get(include=['documents', 'metadatas'])
        
        # Convert to simple format
        news_data = []
        for i, doc in enumerate(all_docs['documents']):
            metadata = all_docs['metadatas'][i] if all_docs['metadatas'] else {}
            
            # Create a user-friendly link text
            link_text = ""
            if metadata.get('link'):
                source = metadata.get('source', 'Unknown Source')
                link_text = f"Read more at {source}"
            
            news_item = {
                "title": metadata.get('title', ''),
                "link": metadata.get('link', ''),
                "link_text": link_text,
                "has_link": bool(metadata.get('link')),
                "content": doc,
                "pub_date": metadata.get('pub_date', ''),
                "source": metadata.get('source', '')
            }
            news_data.append(news_item)
        
        return news_data
        
    except Exception as e:
        return {"error": str(e)}