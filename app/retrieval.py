from app.db import get_connection
from app.embeddings import embed_text

def retrieve_chunks(question: str, top_k: int = 5) -> list[dict]:
    """Embed the question and return the most similar chunks from the database."""
    question_embedding = embed_text(question)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, filename, page, text,
                       embedding <=> %s::vector AS distance
                FROM chunks
                ORDER BY distance
                LIMIT %s
                """,
                (question_embedding, top_k),
            )
            rows = cur.fetchall()

    return [
        {"id": r[0], "filename": r[1], "page": r[2], "text": r[3], "distance": r[4]}
        for r in rows
    ]