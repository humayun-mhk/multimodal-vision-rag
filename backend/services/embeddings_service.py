from config import GEMINI_EMBEDDING_MODEL
from services.gemini_client import get_gemini_client

GEMINI_EMBEDDING_DIMENSION = 3072


def _client():
    return get_gemini_client()


async def get_embedding(text: str) -> list[float]:
    """Generate embedding for a single text string."""
    text = text.replace("\n", " ").strip()
    if not text:
        raise ValueError("Cannot embed empty text")

    response = await _client().embeddings.create(
        model=GEMINI_EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding


async def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of texts."""
    cleaned = [t.replace("\n", " ").strip() for t in texts if t.strip()]
    if not cleaned:
        return []

    response = await _client().embeddings.create(
        model=GEMINI_EMBEDDING_MODEL,
        input=cleaned,
    )
    return [item.embedding for item in response.data]


def get_embedding_dimension() -> int:
    """Return the configured Gemini embedding dimension."""
    return GEMINI_EMBEDDING_DIMENSION
