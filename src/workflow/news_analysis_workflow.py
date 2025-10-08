import os
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from src.rag.vector_store_manager import rag_news
from src.data_sources.wikipedia_search import wiki_search
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.environ["OPENAI_API_KEY"]

class State(TypedDict):
    prompt: str
    rag_doc: str
    wiki_doc: str
    route_choice: str
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

def rag_node(prompt: str) -> str:
    """Function for RAG-based news analysis"""
    retriever = rag_news(prompt)
    docs = retriever.invoke(prompt)
    return "\n\n".join([doc.page_content for doc in docs])

def wiki_node(prompt: str) -> str:
    """Function for Wikipedia search"""
    return wiki_search(prompt)

def writing_node(prompt: str, rag_doc: str = "", wiki_doc: str = "") -> str:
    """Function for generating final response"""
    llm = ChatOpenAI(model='gpt-4o-mini', api_key=openai_api_key, temperature=0)
    
    context = ""
    if rag_doc:
        context += f"Recent News Context:\n{rag_doc}\n\n"
    if wiki_doc:
        context += f"Wikipedia Context:\n{wiki_doc}\n\n"
    
    prompt_template = ChatPromptTemplate.from_template("""
    You are an AI News Analyst. Use the following context to provide a comprehensive response.
    
    Context:
    {context}
    
    User Question: {question}
    
    Provide a detailed, well-structured response that incorporates relevant information from the context.
    """)
    
    chain = (
        {"context": lambda x: context, "question": RunnablePassthrough()}
        | prompt_template
        | llm
        | StrOutputParser()
    )
    
    return chain.invoke(prompt)

def router_node(state: State):
    """Router node that uses the route_decision function"""
    route_choice = route_decision(state['prompt'])
    return {"route_choice": route_choice}

def rag_processing_node(state: State):
    """RAG processing node"""
    rag_doc = rag_node(state['prompt'])
    return {"rag_doc": rag_doc}

def wiki_processing_node(state: State):
    """Wiki processing node"""
    wiki_doc = wiki_node(state['prompt'])
    return {"wiki_doc": wiki_doc}

def final_writing_node(state: State):
    """Final writing node"""
    response = writing_node(
        state['prompt'],
        state.get('rag_doc', ''),
        state.get('wiki_doc', '')
    )
    return {"response": response}

def should_continue(state: State):
    """Determine which path to take based on route_choice"""
    if state['route_choice'] == 'rag':
        return "rag_processing"
    elif state['route_choice'] == 'wiki':
        return "wiki_processing"
    else:
        return "rag_processing"  # Default to RAG

# Create the graph
workflow = StateGraph(State)

# Add nodes
workflow.add_node("router", router_node)
workflow.add_node("rag_processing", rag_processing_node)
workflow.add_node("wiki_processing", wiki_processing_node)
workflow.add_node("writing", final_writing_node)

# Add edges
workflow.add_edge(START, "router")
workflow.add_conditional_edges(
    "router",
    should_continue,
    {
        "rag_processing": "rag_processing",
        "wiki_processing": "wiki_processing"
    }
)
workflow.add_edge("rag_processing", "writing")
workflow.add_edge("wiki_processing", "writing")
workflow.add_edge("writing", END)

# Compile the graph
app = workflow.compile()

def run_news_analysis(prompt: str):
    """Run the complete news analysis workflow using tools"""
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