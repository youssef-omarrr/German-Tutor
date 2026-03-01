from tavily import TavilyClient
from dotenv import load_dotenv
import os
from langchain_core .tools import tool

# load .env file to get access keys
load_dotenv()

client = TavilyClient(os.getenv("TAVILY_API_KEY"))

@tool
def search_web(query:str) -> str: 
    """
    Use this to search the internet for current events, facts, news, 
    or any question that needs up-to-date information not available in a textbook.
    """
    response = client.search(
        query=query,
        include_answer="basic",
        search_depth="basic",
        max_results=3
    )
    
    return response["answer"]

# ========================================================================
#                           USAGE EXAMPLES
# ========================================================================

if __name__ == "__main__":
    # Example RAG responses
    
    response = search_web(
        query= "who is the latest champions league winner",
    )
    
    print(response)
    print("\n\n\n")
    print(response["answer"])