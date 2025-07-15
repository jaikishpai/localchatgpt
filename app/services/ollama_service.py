import ollama

# You may need to configure the base_url or model name depending on your Ollama setup
OLLAMA_MODEL = 'llama2'  # Change to your preferred model


def get_ollama_response(prompt: str, context: str = "") -> str:
    full_prompt = f"Context:\n{context}\n\nUser: {prompt}\nAnswer:"
    response = ollama.chat(model=OLLAMA_MODEL, messages=[{"role": "user", "content": full_prompt}])
    return response['message']['content'] 