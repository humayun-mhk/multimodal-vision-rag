import re


GREETING_PATTERN = re.compile(
    r"^(?:hi+|hello+|hallo+|hey+|hiya|howdy|good\s+(?:morning|afternoon|evening))[!.?\s]*$",
    re.IGNORECASE,
)


def is_greeting(value: str) -> bool:
    return bool(GREETING_PATTERN.fullmatch(value.strip()))


def plain_text(value: str | None) -> str:
    """Remove Markdown bold markers unsupported by the plain-text chat UI."""
    return (value or "").replace("**", "").strip()
