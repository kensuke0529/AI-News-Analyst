from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

def wiki_search(topic):
    wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
    wiki_doc = wikipedia.run(topic)
    return wiki_doc

