from .semantic_search import index_pdfs, semantic_search

# Simple keyword search for relevant PDF content
def search_knowledge_base(query: str, max_results: int = 3) -> list:
    pdf_texts = load_all_pdfs()
    results = []
    for filename, text in pdf_texts.items():
        if query.lower() in text.lower():
            snippet = text.lower().split(query.lower(), 1)[-1][:500]  # Get 500 chars after match
            results.append((filename, snippet))
            if len(results) >= max_results:
                break
    return results 