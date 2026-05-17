from config import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Split text into overlapping chunks for better semantic retrieval.
    Uses word-boundary splitting.
    """
    if not text or not text.strip():
        return []

    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk.strip())
        start += chunk_size - overlap

    return chunks


def clean_text(text: str) -> str:
    """Remove excessive whitespace, null bytes, and normalize newlines."""
    if not text:
        return ""
    text = text.replace("\x00", "")
    text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    return text.strip()
