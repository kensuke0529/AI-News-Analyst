from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from src.workflow.news_analysis_workflow import run_news_analysis
from src.rag.database_manager import db_manager
import os
import json
import tiktoken
from datetime import datetime, date
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

# Global token tracking
TOKEN_USAGE_FILE = "storage/daily_token_usage.json"
DAILY_TOKEN_LIMIT = 5000  # 5000 tokens per day

def load_daily_usage():
    """Load today's token usage from file"""
    try:
        with open(TOKEN_USAGE_FILE, 'r') as f:
            data = json.load(f)
            today = date.today().isoformat()
            return data.get(today, 0)
    except FileNotFoundError:
        return 0

def save_daily_usage(tokens_used):
    """Save today's token usage to file"""
    try:
        with open(TOKEN_USAGE_FILE, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    
    today = date.today().isoformat()
    data[today] = data.get(today, 0) + tokens_used
    
    with open(TOKEN_USAGE_FILE, 'w') as f:
        json.dump(data, f)

def count_tokens(text: str) -> int:
    """Count tokens in text using tiktoken"""
    try:
        encoding = tiktoken.encoding_for_model("gpt-4o-mini")
        return len(encoding.encode(text))
    except:
        # Fallback: rough estimate (1 token ≈ 4 characters)
        return len(text) // 4

class NewsQuery(BaseModel):
    query: str

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def root():
    """Serve the frontend HTML file"""
    return FileResponse("frontend/index.html")

@app.get("/health")
def health_check():
    """Health check endpoint for Railway"""
    try:
        # Basic health check - just return success
        return {
            "status": "healthy", 
            "message": "AI News Analyst is running",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        # If there's any error, return unhealthy status
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.get("/api/status")
def get_status():
    """Get current token usage status"""
    current_usage = load_daily_usage()
    remaining = max(0, DAILY_TOKEN_LIMIT - current_usage)
    
    return {
        "daily_limit": DAILY_TOKEN_LIMIT,
        "used_today": current_usage,
        "remaining_today": remaining,
        "percentage_used": round((current_usage / DAILY_TOKEN_LIMIT) * 100, 2),
        "status": "available" if remaining > 0 else "limit_reached"
    }

@app.post("/api/news/rag")
def rag_news(news_query: NewsQuery):
    # Check if we've hit the daily limit
    current_usage = load_daily_usage()
    
    if current_usage >= DAILY_TOKEN_LIMIT:
        raise HTTPException(
            status_code=429, 
            detail={
                "error": "Daily token limit reached",
                "limit": DAILY_TOKEN_LIMIT,
                "used": current_usage,
                "message": "The site has reached its daily token limit. Please try again tomorrow."
            }
        )
    
    # Estimate tokens for this request
    query_tokens = count_tokens(news_query.query)
    estimated_response_tokens = 500  # Conservative estimate
    
    # Check if this request would exceed the limit
    if current_usage + query_tokens + estimated_response_tokens > DAILY_TOKEN_LIMIT:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Request would exceed daily limit",
                "remaining_tokens": DAILY_TOKEN_LIMIT - current_usage,
                "estimated_tokens_needed": query_tokens + estimated_response_tokens
            }
        )
    
    try:
        # Process the request
        result = run_news_analysis(news_query.query)
        
        # Count actual tokens used
        response_tokens = count_tokens(result)
        total_tokens = query_tokens + response_tokens
        
        # Save usage
        save_daily_usage(total_tokens)
        
        # Get updated status
        new_usage = load_daily_usage()
        remaining = max(0, DAILY_TOKEN_LIMIT - new_usage)
        
        return {
            "response": result,
            "tokens_used": total_tokens,
            "remaining_today": remaining,
            "status": "available" if remaining > 0 else "limit_reached"
        }
        
    except Exception as e:
        # If there's an error, still count the query tokens
        save_daily_usage(query_tokens)
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/api/news/all')
def get_news():
    try:
        # Get all documents using the database manager
        all_docs = db_manager.get_all_documents()
        
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