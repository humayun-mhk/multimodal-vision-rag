import numpy as np
from openai import AsyncOpenAI
from config import OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def get_embedding(text: str) -> list[float]:
    """Generate embedding for a single text string."""
    text = text.replace("\n", " ").strip()
    if not text:
        raise ValueError("Cannot embed empty text")

    response = await client.embeddings.create(
        model=OPENAI_EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding


async def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of texts."""
    cleaned = [t.replace("\n", " ").strip() for t in texts if t.strip()]
    if not cleaned:
        return []

    response = await client.embeddings.create(
        model=OPENAI_EMBEDDING_MODEL,
        input=cleaned
    )
    return [item.embedding for item in response.data]


def get_embedding_dimension() -> int:
    """Return the dimension for text-embedding-3-small."""
    return 1536
