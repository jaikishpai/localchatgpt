from app.main import app

@app.get("/health")
def health_check():
    return {"status": "ok"} 