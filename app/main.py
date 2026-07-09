from fastapi import FastAPI, UploadFile, File, HTTPException
from app.ingest import extract_text_from_pdf, chunk_text 


app = FastAPI(title="DocuChat API")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    file_bytes = await file.read()
    pages = extract_text_from_pdf(file_bytes)

    if not pages:
        raise HTTPException(status_code=400, detail="No text could be extracted from this PDF")

    all_chunks = []
    for page in pages:
        for chunk in chunk_text(page["text"]):
            all_chunks.append({"page": page["page"], "text": chunk})

    return {
        "filename": file.filename,
        "pages_extracted": len(pages),
        "chunks_created": len(all_chunks),
        "sample_chunk": all_chunks[0]["text"][:200] if all_chunks else None,
    }
