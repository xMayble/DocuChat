from sentence_transformers import SentenceTransformer

# Loaded once when the app starts
_model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_text(text: str) -> list[float]:
    """Turn a single string into a 384-dimension embedding."""
    return _model.encode(text).tolist()

def embed_batch(texts: list[str]) -> list[list[float]]:
    """Embed many strings at once (more efficient)."""
    return _model.encode(texts).tolist()