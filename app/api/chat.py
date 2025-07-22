from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services.ollama_service import get_ollama_response
from app.knowledge_base import semantic_search, index_pdfs
from app.services.mongo_service import get_cached_response, cache_response
from app.api.auth import get_current_user

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    context: str = ""

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest, user=Depends(get_current_user)):
    username = user["username"]
    # Check MongoDB cache first
    cached_response, cached_context = get_cached_response(username, request.message)
    if cached_response:
        return ChatResponse(response=cached_response, context=cached_context)
    # Semantic search for relevant context
    kb_results = semantic_search(request.message)
    context = "\n---\n".join(f"From {fname}: {snippet}" for fname, snippet in kb_results) if kb_results else ""
    response_text = get_ollama_response(request.message, context)
    # Cache the result
    cache_response(username, request.message, response_text, context)
    return ChatResponse(response=response_text, context=context)

@router.post("/index_pdfs")
def trigger_indexing():
    index_pdfs()
    return {"status": "PDFs indexed"} 