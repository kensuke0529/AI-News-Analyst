import os
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.rag.database_manager import db_manager
from src.data_sources.wikipedia_search import wiki_search
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.environ["OPENAI_API_KEY"]

class State(TypedDict):
    prompt: str
    route_choice: str
    retrieved_docs: str
    response: str

def route_decision(prompt: str) -> str:
    """
    Function to determine whether to use RAG or Wikipedia based on the user prompt.
    For a news analysis site, we should prioritize RAG for most queries.
    """
    # For a news analysis site, we should almost always use RAG
    # Only use Wikipedia for very specific general knowledge questions
    
    # Check if the prompt is asking for very general knowledge that's not news-related
    general_knowledge_keywords = [
        "what is", "define", "explain the concept", "how does work", 
        "definition of", "meaning of", "explain", "describe"
    ]
    
    # If it's a very general knowledge question, use Wikipedia
    if any(keyword in prompt.lower() for keyword in general_knowledge_keywords):
        # But still check if it's news-related
        news_keywords = [
            "news", "recent", "latest", "current", "today", "yesterday", 
            "this week", "this month", "breaking", "update", "announcement"
        ]
        
        # If it contains news keywords, use RAG
        if any(keyword in prompt.lower() for keyword in news_keywords):
            return "rag"
        
        # Otherwise, use Wikipedia for general knowledge
        return "wiki"
    
    # For all other queries, use RAG (news analysis site)
    return "rag"

def query_vector_db(prompt: str, persist_directory="./data/vector_db") -> str:
    """
    Query the pre-populated vector DB - NO extraction/fetching here.
    This assumes the DB has been populated by the background extraction job.
    """
    # Use the database manager to search for relevant documents
    results = db_manager.search_documents(prompt, k=3)
    
    # Format with metadata for better attribution
    formatted_docs = []
    for result in results:
        metadata = result['metadata']
        content = result['content']
        source = metadata.get('source', 'unknown')
        title = metadata.get('title', '')
        link = metadata.get('link','')
        pub_date = metadata.get('pub_date', '')
        
        # Format with clear source attribution
        formatted_docs.append(
            f"SOURCE: {source}\nTITLE: {title}\nDATE: {pub_date}\nLINK: {link}\nCONTENT: {content}"
        )
    
    return "\n\n---\n\n".join(formatted_docs)

def wiki_node(prompt: str) -> str:
    """Function for Wikipedia search"""
    return wiki_search(prompt)

def router_node(state: State):
    """Router node that uses the route_decision function"""
    route_choice = route_decision(state['prompt'])
    return {"route_choice": route_choice}

def rag_query_node(state: State):
    """Query pre-populated vector DB - NO extraction"""
    docs = query_vector_db(state['prompt'])
    return {"retrieved_docs": docs}

def wiki_query_node(state: State):
    """Query Wikipedia"""
    docs = wiki_node(state['prompt'])
    return {"retrieved_docs": docs}

def response_generation_node(state: State):
    """Generate response from retrieved documents"""
    llm = ChatOpenAI(model='gpt-4o-mini', api_key=openai_api_key, temperature=0)
    
    prompt_template = ChatPromptTemplate.from_template("""
    You are an AI News Analyst. Use the following context to provide a comprehensive response.
    
    Context:
    {context}
    
    User Question: {question}
    
    CRITICAL RULES:
    1. ONLY use information from the provided context above
    2. DO NOT make up or hallucinate any information not in the context
    3. DO NOT cite sources that are not explicitly mentioned in the context
    4. If the context doesn't contain enough information to answer the question, say so clearly
    
    SOURCE CITATION RULES:
    1. ONLY cite sources that are explicitly mentioned in the context above
    2. Use the exact source names and links provided in the context
    3. If no sources are provided in the context, do NOT add any citations
    4. NEVER make up source names like "The Record" or "Suzanne Smalley" unless they appear in the context
    5. When citing, use markdown format: [Source Name](URL) where both the name and URL come from the context
    
    Provide a detailed, well-structured response that incorporates relevant information from the context.
    If the context doesn't contain enough information, clearly state what information is missing.
    """)
    
    chain = (
        {
            "context": lambda x: state['retrieved_docs'], 
            "question": lambda x: state['prompt']
        }
        | prompt_template
        | llm
        | StrOutputParser()
    )
    
    response = chain.invoke({})
    return {"response": response}

def should_continue(state: State):
    """Determine which path to take based on route_choice"""
    return "rag_query" if state['route_choice'] == 'rag' else "wiki_query"

# Create the graph
workflow = StateGraph(State)

# Add nodes
workflow.add_node("router", router_node)
workflow.add_node("rag_query", rag_query_node)
workflow.add_node("wiki_query", wiki_query_node)
workflow.add_node("generate_response", response_generation_node)

# Add edges
workflow.add_edge(START, "router")
workflow.add_conditional_edges(
    "router",
    should_continue,
    {
        "rag_query": "rag_query",
        "wiki_query": "wiki_query"
    }
)
workflow.add_edge("rag_query", "generate_response")
workflow.add_edge("wiki_query", "generate_response")
workflow.add_edge("generate_response", END)

# Compile the graph
app = workflow.compile()

def run_news_analysis(prompt: str):
    """
    Run query-only news analysis workflow.
    Note: This assumes the vector DB has been pre-populated by the extraction job.
    """
    result = app.invoke({"prompt": prompt})
    return result['response']

if __name__ == "__main__":
    try:
        user_input = input("Enter your prompt: ")
        prompt = user_input
        result = run_news_analysis(prompt)
        print("=== AI Response ===")
        print(result)
    except EOFError:
        # Handle case when running in non-interactive environment
        print("Please run this script interactively to enter your prompt.")