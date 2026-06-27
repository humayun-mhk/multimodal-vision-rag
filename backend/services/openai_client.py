import os

from openai import AsyncOpenAI

from config import OPENAI_API_KEY

_client: AsyncOpenAI | None = None
_client_key: str | None = None


def _clean_api_key(value: str | None) -> str:
    return (value or "").strip().strip('"').strip("'")


def get_openai_api_key() -> str:
    return _clean_api_key(os.getenv("OPENAI_API_KEY") or OPENAI_API_KEY)


def is_openai_configured() -> bool:
    return bool(get_openai_api_key())


def get_openai_client() -> AsyncOpenAI:
    global _client, _client_key

    api_key = get_openai_api_key()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    if _client is None or _client_key != api_key:
        _client = AsyncOpenAI(api_key=api_key)
        _client_key = api_key

    return _client
