from fastapi import FastAPI, UploadFile, File, HTTPException
from app.ingest import extract_text_from_pdf, chunk_text 
from app.db import get_connection
from app.embeddings import embed_batch 
from app.retrieval import retrieve_chunks
from app.answer import answer_question
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware 


app = FastAPI(title="DocuChat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for local dev; tighten before deploying
    allow_methods=["*"],
    allow_headers=["*"],
)

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

    # Generate embeddings for every chunk at once
    texts = [c["text"] for c in all_chunks]
    embeddings = embed_batch(texts)

    # Store each chunk with its embedding in the database
    with get_connection() as conn:
        with conn.cursor() as cur:
            for chunk, embedding in zip(all_chunks, embeddings):
                cur.execute(
                    "INSERT INTO chunks (filename, page, text, embedding) VALUES (%s, %s, %s, %s)",
                    (file.filename, chunk["page"], chunk["text"], embedding),
                )
        conn.commit()

    return {
        "filename": file.filename,
        "pages_extracted": len(pages),
        "chunks_stored": len(all_chunks),
    }

class AskRequest(BaseModel):
    question: str

@app.post("/ask")
def ask(request: AskRequest):
    chunks = retrieve_chunks(request.question, top_k=5)
    if not chunks:
        raise HTTPException(status_code=404, detail="No documents have been uploaded yet")

    answer = answer_question(request.question, chunks)
    return {
        "question": request.question,
        "answer": answer,
        "sources": [
            {"chunk": i + 1, "page": c["page"], "filename": c["filename"]}
            for i, c in enumerate(chunks)
        ],
    }
    
