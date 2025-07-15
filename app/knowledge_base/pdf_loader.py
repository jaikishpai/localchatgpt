import os
from pypdf import PdfReader

KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'knowledge_base')


def load_all_pdfs() -> dict:
    """Load and extract text from all PDFs in the knowledge_base directory."""
    pdf_texts = {}
    for filename in os.listdir(KNOWLEDGE_BASE_DIR):
        if filename.lower().endswith('.pdf'):
            path = os.path.join(KNOWLEDGE_BASE_DIR, filename)
            try:
                reader = PdfReader(path)
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
                pdf_texts[filename] = text
            except Exception as e:
                pdf_texts[filename] = f"Error reading PDF: {e}"
    return pdf_texts 