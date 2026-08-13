from google.genai import types

from config import GEMINI_EMBEDDING_MODEL
from services.gemini_client import get_gemini_client

GEMINI_EMBEDDING_DIMENSION = 1536

def _client():
    return get_gemini_client()


async def get_embedding(text: str) -> list[float]:
    """Generate embedding for a single text string."""
    text = text.replace("\n", " ").strip()
    if not text:
        raise ValueError("Cannot embed empty text")

    response = await _client().aio.models.embed_content(
        model=GEMINI_EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=GEMINI_EMBEDDING_DIMENSION,
        ),
    )
    return response.embeddings[0].values


async def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of texts."""
    cleaned = [t.replace("\n", " ").strip() for t in texts if t.strip()]
    if not cleaned:
        return []

    response = await _client().aio.models.embed_content(
        model=GEMINI_EMBEDDING_MODEL,
        contents=cleaned,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=GEMINI_EMBEDDING_DIMENSION,
        ),
    )
    return [item.values for item in response.embeddings]


def get_embedding_dimension() -> int:
    """Return the configured Gemini embedding dimension."""
    return GEMINI_EMBEDDING_DIMENSION
