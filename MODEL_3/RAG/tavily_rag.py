from tavily import TavilyClient
from dotenv import load_dotenv
import os

# load .env file t0 get access keys
load_dotenv()


def search_web(query:str,
            include_answer:str = "basic",
            search_depth:str = "basic",
            max_results:int = 3,):
    
    client = TavilyClient(os.getenv("TAVILY_API_KEY"))
    
    response = client.search(
        query=query,
        include_answer=include_answer,
        search_depth=search_depth,
        max_results=max_results
    )
    
    return response

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