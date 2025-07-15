from fastapi import APIRouter
from pydantic import BaseModel
from app.services.ollama_service import get_ollama_response
from app.knowledge_base import semantic_search, index_pdfs

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    context: str = ""

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    # Semantic search for relevant context
    kb_results = semantic_search(request.message)
    context = "\n---\n".join(f"From {fname}: {snippet}" for fname, snippet in kb_results) if kb_results else ""
    response_text = get_ollama_response(request.message, context)
    return ChatResponse(response=response_text, context=context)

@router.post("/index_pdfs")
def trigger_indexing():
    index_pdfs()
    return {"status": "PDFs indexed"} 