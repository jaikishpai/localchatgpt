from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.knowledge_base.url_loader import fetch_url_text
from app.knowledge_base.semantic_search import chunk_text, model, collection
from app.api.auth import get_current_user
import hashlib

router = APIRouter()

class AddUrlRequest(BaseModel):
    url: str

@router.post("/add_url")
def add_url(req: AddUrlRequest, user=Depends(get_current_user)):
    try:
        text = fetch_url_text(req.url)
        if not text or len(text) < 100:
            raise HTTPException(status_code=400, detail="URL content too short or empty.")
        chunks = chunk_text(text)
        embeddings = model.encode(chunks).tolist()
        url_hash = hashlib.sha256(req.url.encode()).hexdigest()
        ids = [f"url_{url_hash}_{i}" for i in range(len(chunks))]
        metadatas = [{"url": req.url, "chunk": i} for i in range(len(chunks))]
        collection.add(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)
        return {"status": "URL added and indexed", "chunks": len(chunks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add URL: {e}")
