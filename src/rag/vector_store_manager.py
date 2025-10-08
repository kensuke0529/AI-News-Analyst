from src.data_sources.techmeme_rss_parser import *
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Suppress SSL warnings completely
warnings.filterwarnings('ignore', category=urllib3.exceptions.NotOpenSSLWarning)
os.environ['PYTHONWARNINGS'] = 'ignore::urllib3.exceptions.NotOpenSSLWarning'

load_dotenv()
openai_api_key = os.environ["OPENAI_API_KEY"]
techmeme_rss = "https://www.techmeme.com/feed.xml"

def rag_news(user_prompt):
    # Embedding news and store to vector db
    vector_store = Embedding_news()
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