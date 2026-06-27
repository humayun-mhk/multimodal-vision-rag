import os
from dotenv import load_dotenv

load_dotenv()


def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got {raw!r}") from exc


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_VISION_MODEL = os.getenv("OPENAI_VISION_MODEL", "gpt-4o")
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./data/faiss_index")
CHUNK_SIZE = _get_int("CHUNK_SIZE", 500)
CHUNK_OVERLAP = _get_int("CHUNK_OVERLAP", 50)
TOP_K = _get_int("TOP_K", 5)
PORT = _get_int("PORT", 8000)

_cors_origins = os.getenv("CORS_ORIGINS", "*")
CORS_ORIGINS = [origin.strip() for origin in _cors_origins.split(",") if origin.strip()]

