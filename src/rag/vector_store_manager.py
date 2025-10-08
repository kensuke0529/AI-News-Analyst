from src.data_sources.techmeme_rss_parser import get_text as get_techmeme_text
from src.data_sources.mit import get_text as get_mit_text
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain.schema import Document
import warnings
import urllib3
import os
from dotenv import load_dotenv

# Suppress SSL warnings completely
warnings.filterwarnings('ignore', category=urllib3.exceptions.NotOpenSSLWarning)
os.environ['PYTHONWARNINGS'] = 'ignore::urllib3.exceptions.NotOpenSSLWarning'

load_dotenv()
openai_api_key = os.environ["OPENAI_API_KEY"]
embedding_model = OpenAIEmbeddings(api_key=openai_api_key, model="text-embedding-3-small")

def rag_news(user_prompt, persist_directory="./data/vector_db"):
    """
    Create or update vector store with articles from multiple sources (Techmeme and MIT).
    """
    print("=== Searching Related news from multiple sources ===")
    
    # Get articles from both sources
    techmeme_articles = get_techmeme_text()
    mit_articles = get_mit_text()
    all_articles = techmeme_articles + mit_articles
    
    splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", ""],
        chunk_size=500,
        chunk_overlap=10
    )

    # Try to load existing vector store
    try:
        vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding_model
        )
        # Get existing article links to avoid duplicates
        existing_links = set()
        try:
            all_docs = vector_store.get()
            if all_docs and 'metadatas' in all_docs:
                existing_links = {doc['link'] for doc in all_docs['metadatas'] if 'link' in doc}
        except:
            existing_links = set()
    except:
        vector_store = None
        existing_links = set()

    # Filter out articles that already exist
    new_articles = [article for article in all_articles if article['link'] not in existing_links]
    
    if not new_articles:
        print("No new articles to add.")
        if vector_store is None:
            vector_store = Chroma(
                persist_directory=persist_directory,
                embedding_function=embedding_model
            )
        retriever = vector_store.as_retriever(
            search_type='similarity', search_kwargs={"k":3}
        )
        return retriever

    print(f"Adding {len(new_articles)} new articles to vector store.")
    
    # Group articles by source for reporting
    sources_count = {}
    for article in new_articles:
        source = article.get('source', 'unknown')
        sources_count[source] = sources_count.get(source, 0) + 1
    print(f"New articles by source: {sources_count}")

    all_docs = []

    for article in new_articles:
        news_content = f"Title: {article['title']}, Content: {article['description']}"
        chunks = splitter.split_text(news_content)

        doc_objs = [
            Document(
                page_content=chunk,
                metadata={
                    "title": article["title"],
                    "link": article["link"],
                    "pub_date": article["pub_date"],
                    "source": article["source"]
                }
            )
            for chunk in chunks
        ]

        all_docs.extend(doc_objs)

    if vector_store is None:
        vector_store = Chroma.from_documents(
            documents=all_docs,
            embedding=embedding_model,
            persist_directory=persist_directory
        )
    else:
        vector_store.add_documents(all_docs)

    retriever = vector_store.as_retriever(
        search_type='similarity', search_kwargs={"k":3}
    )
    
    return retriever

    # # RAG / LLM response
    # prompt = ChatPromptTemplate.from_template("""
    # Use the following pieces of context to answer the question at the end.
    # If you don't know the answer, say that you don't know.
    # Context: {context}
    # Question: {question}  
    # """)

    # llm = ChatOpenAI(model='gpt-4o-mini', api_key=openai_api_key, temperature=0)

    # def format_docs(docs):
    #     return "\n\n".join(doc.page_content for doc in docs)

    # app = (
    #     {"context": retriever | format_docs, "question": RunnablePassthrough()}
    #     | prompt
    #     | llm
    #     | StrOutputParser()
    # )

    # result = app.invoke(user_prompt)
    # print('=== AI Response ===')
    # print(result)