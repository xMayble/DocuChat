from pypdf import PdfReader
from io import BytesIO

def extract_text_from_pdf(file_bytes: bytes) -> list[dict]:
    """Extract text from a PDF, returning one entry per page."""
    reader = PdfReader(BytesIO(file_bytes))
    pages = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip(): #skip blank pages
            pages.append({"page": page_number, "text":text})
    return pages