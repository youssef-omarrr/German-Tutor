from pathlib import Path
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. embedding
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

# 2. load pdf
PDF_PATH = Path(__file__).parent / "books" / "Fsi-GermanBasicCourse-Volume2-StudentText.pdf"

# 3. Checks if the PDF is there and load pages
if not PDF_PATH.exists():
    print(f"PDF not found at: {PDF_PATH}")
    raise FileNotFoundError(f"PDF not found at: {PDF_PATH}")

pdf_loader = PyPDFLoader(str(PDF_PATH))

try:
    pages = pdf_loader.load()
    print(f"PDF has been loaded and has {len(pages)} pages")
except Exception as e:
    print(f"Error loading PDF: {e}")
    raise

# 4. chunk the pdf
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=300
)

# 5. apply text splitter to our pages
pages_split = text_splitter.split_documents(pages)

# 6. save the chroma db
SAVE_DIR = r"C:\Users\YOUSSEF\Desktop\Codess & Projects\German Tutor\MODEL_3\RAG\db"

try:
    vector_store = Chroma.from_documents(
        documents = pages_split,
        embedding = embeddings,
        persist_directory = SAVE_DIR,
        collection_name = "German_Books"
    )
    print(f"Created ChromaDB vector store!")
    
except Exception as e:
    print(f"Error setting up ChromaDB: {str(e)}")
    raise