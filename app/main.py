from fastapi import FastAPI, UploadFile, File, HTTPException
from app.ingest import extract_text_from_pdf

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
        raise HTTPException(status_code=400, detail=400, detail="No text could be extracted from this PDF")

    total_chars = sum(len(p["text"]) for p in pages)
    return {
        "filename": file.filename,
        "pages_extracted": len(pages),
        "total_characters": total_chars,
    }
