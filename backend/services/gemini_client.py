import os

from google import genai

from config import GOOGLE_API_KEY

_client: genai.Client | None = None
_client_key: str | None = None


def _clean_api_key(value: str | None) -> str:
    return (value or "").strip().strip('"').strip("'")


def get_google_api_key() -> str:
    return _clean_api_key(
        os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or GOOGLE_API_KEY
    )


def is_gemini_configured() -> bool:
    return bool(get_google_api_key())


def get_gemini_client() -> genai.Client:
    global _client, _client_key

    api_key = get_google_api_key()
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is not configured")

    if _client is None or _client_key != api_key:
        _client = genai.Client(api_key=api_key)
        _client_key = api_key

    return _client
