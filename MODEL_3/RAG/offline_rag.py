from langchain_core.tools import tool
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 1. load vectorized database
vector_store = Chroma(
    persist_directory=r"C:\Users\YOUSSEF\Desktop\Codess & Projects\German Tutor\MODEL_3\RAG\db",
    embedding_function=embeddings,
    collection_name="German_Books"
)

# 2. create retriver
retriever = vector_store.as_retriever(
    search_type = "similarity",
    search_kwargs={"k": 5} # K is the amount of chunks to return
)

@tool
def search_local_books(query:str) -> str :
    """
    This tool searches and returns the information from:
        1. A-Foundation-Course-in-Reading-German.pdf 
        2. Fsi-GermanBasicCourse-Volume1-StudentText.pdf
        3. Fsi-GermanBasicCourse-Volume2-StudentText.pdf 
    """
    docs = retriever.invoke(query)
    
    if not docs:
        return "I found no relevant information in the DataBase"
    
    results = []
    for i, doc in enumerate(docs):
        results.append(f"Document {i+1}:\n{doc.page_content}")
    
    return "\n\n".join(results)

