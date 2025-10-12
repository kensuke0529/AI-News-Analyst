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
    Returns 'rag' for recent news/current events, 'wiki' for general knowledge.
    """
    llm = ChatOpenAI(model='gpt-4o-mini', api_key=openai_api_key, temperature=0)
    
    routing_prompt = f"""
    Analyze this user prompt and determine the best approach:
    
    Prompt: {prompt}
    
    Return "rag" if this is about recent news, current events, or requires up-to-date information.
    Return "wiki" if this is about general knowledge, historical facts, or established concepts.
    
    Only return "rag" or "wiki" - nothing else.
    """
    
    response = llm.invoke(routing_prompt)
    return response.content.strip().lower()

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
        formatted_docs.append(
            f"[{source} - {pub_date}] {title}\nLink: {link}\n{content}"
        )
    
    return "\n\n".join(formatted_docs)

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
    
    Provide a detailed, well-structured response that incorporates relevant information from the context.
    
    CRITICAL FORMATTING RULES FOR SOURCES:
    1. When citing sources, use markdown hyperlink format: [Source Name](URL)
    2. The URL should be completely hidden - users should only see the source name
    3. Use clean source names like "Suzanne Smalley, The Record" or "The Record"
    4. NEVER show the actual URL text anywhere in your response
    5. Example: Write [Suzanne Smalley, The Record](http://www.techmeme.com/251008/p28#a251008p28) - users will only see "Suzanne Smalley, The Record" as clickable text
    6. The hyperlink should be invisible to users - they only see the source name
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