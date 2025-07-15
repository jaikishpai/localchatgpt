import os
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'knowledge_base')
CHUNK_SIZE = 500  # characters

# Initialize embedding model and ChromaDB client
model = SentenceTransformer('./model', trust_remote_code=True)
chroma_client = chromadb.Client(Settings(persist_directory=".chroma_db"))
collection = chroma_client.get_or_create_collection("pdf_chunks")

os.environ["CURL_CA_BUNDLE"] = ""
os.environ["TRANSFORMERS_VERIFIED_SSL"] = "false"
os.environ["HF_HUB_DISABLE_SSL_VERIFICATION"] = "1"

def chunk_text(text, chunk_size=CHUNK_SIZE):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def index_pdfs():
    """Load PDFs, split into chunks, embed, and store in ChromaDB."""
    for filename in os.listdir(KNOWLEDGE_BASE_DIR):
        if filename.lower().endswith('.pdf'):
            path = os.path.join(KNOWLEDGE_BASE_DIR, filename)
            try:
                reader = PdfReader(path)
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
                chunks = chunk_text(text)
                embeddings = model.encode(chunks).tolist()
                ids = [f"{filename}_{i}" for i in range(len(chunks))]
                metadatas = [{"filename": filename, "chunk": i} for i in range(len(chunks))]
                collection.add(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)
            except Exception as e:
                print(f"Error indexing {filename}: {e}")

def semantic_search(query, top_k=3):
    query_emb = model.encode([query])[0].tolist()
    results = collection.query(query_embeddings=[query_emb], n_results=top_k)
    matches = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        matches.append((meta["filename"], doc))
    return matches 