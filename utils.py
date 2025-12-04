from sentence_transformers import SentenceTransformer
from typing import List

# Initialize the SentenceTransformer model (same as used for embeddings)
_model = None

def get_embedding_model():
    """Get or initialize the SentenceTransformer model."""
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def get_embedding(text: str) -> List[float]:
    """Generate embedding for text using SentenceTransformer."""
    model = get_embedding_model()
    embedding = model.encode(text, convert_to_numpy=True).tolist()
    return embedding
