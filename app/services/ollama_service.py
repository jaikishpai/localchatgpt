import requests
import json

OLLAMA_BASE_URL = "http://ollama:11434"
OLLAMA_MODEL = "llama2:latest"

def get_ollama_response(prompt: str, context: str = "") -> str:
    full_prompt = f"Context:\n{context}\n\nUser: {prompt}\nAnswer:"
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": full_prompt}]
    }
    try:
        response = requests.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload, stream=True, timeout=180)
        response.raise_for_status()
        answer = ""
        for line in response.iter_lines():
            if not line:
                continue
            data = json.loads(line)
            if "message" in data and "content" in data["message"]:
                answer += data["message"]["content"]
            if data.get("done", False):
                break
        if answer:
            return answer
        else:
            raise ValueError(f"No answer in Ollama response: {data}")
    except Exception as e:
        print(f"Ollama API error: {e}")
        return "Sorry, there was an error processing your request with the LLM." 