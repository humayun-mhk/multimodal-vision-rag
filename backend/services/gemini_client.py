import os

from openai import AsyncOpenAI

from config import GOOGLE_API_KEY

GEMINI_OPENAI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

_client: AsyncOpenAI | None = None
_client_key: str | None = None


def _clean_api_key(value: str | None) -> str:
    return (value or "").strip().strip('"').strip("'")


def get_google_api_key() -> str:
    return _clean_api_key(
        os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or GOOGLE_API_KEY
    )


def is_gemini_configured() -> bool:
    return bool(get_google_api_key())


def get_gemini_client() -> AsyncOpenAI:
    global _client, _client_key

    api_key = get_google_api_key()
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is not configured")

    if _client is None or _client_key != api_key:
        _client = AsyncOpenAI(api_key=api_key, base_url=GEMINI_OPENAI_BASE_URL)
        _client_key = api_key

    return _client
