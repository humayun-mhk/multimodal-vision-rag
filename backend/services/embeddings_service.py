from google import genai
from google.genai import types

from config import GEMINI_EMBEDDING_MODEL
from services.gemini_client import get_google_api_key

GEMINI_EMBEDDING_DIMENSION = 1536

_embedding_client: genai.Client | None = None
_embedding_client_key: str | None = None


def _client():
    global _embedding_client, _embedding_client_key

    api_key = get_google_api_key()
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is not configured")

    if _embedding_client is None or _embedding_client_key != api_key:
        _embedding_client = genai.Client(api_key=api_key)
        _embedding_client_key = api_key

    return _embedding_client


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
