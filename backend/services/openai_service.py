import base64
import json
from openai import AsyncOpenAI
from config import OPENAI_API_KEY, OPENAI_VISION_MODEL

client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def _client() -> AsyncOpenAI:
    if client is None:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    return client


def encode_image_to_base64(image_bytes: bytes) -> str:
    """Convert image bytes to base64 string."""
    return base64.b64encode(image_bytes).decode("utf-8")


async def extract_from_image(image_bytes: bytes, filename: str = "image") -> dict:
    """
    Use GPT-4o vision to extract structured content from an image.
    Returns: { text, summary, entities }
    """
    b64_image = encode_image_to_base64(image_bytes)

    system_prompt = """You are an expert document and image analyzer.
Extract all readable text and meaningful information from the provided image.
Respond ONLY with valid JSON in this exact format:
{
  "text": "full extracted text from image",
  "summary": "concise 2-3 sentence summary of content",
  "entities": ["list", "of", "key", "entities", "found"]
}"""

    response = await _client().chat.completions.create(
        model=OPENAI_VISION_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{b64_image}",
                            "detail": "high"
                        }
                    },
                    {
                        "type": "text",
                        "text": f"Extract all content from this image (filename: {filename}). Return valid JSON only."
                    }
                ]
            }
        ],
        max_tokens=2000,
        temperature=0.1
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        return json.loads(raw.strip())
    except json.JSONDecodeError:
        # Fallback: return raw text as-is
        return {
            "text": raw,
            "summary": f"Content extracted from {filename}",
            "entities": []
        }


async def answer_with_context(query: str, context_chunks: list[str]) -> str:
    """
    Send user query + retrieved context to GPT-4o for a final answer.
    """
    context_text = "\n\n---\n\n".join(
        [f"[Chunk {i+1}]:\n{chunk}" for i, chunk in enumerate(context_chunks)]
    )

    system_prompt = """You are a helpful AI assistant with access to documents uploaded by the user.
Use the provided context chunks to answer the question accurately.
If the answer is not found in the context, say so clearly.
Be concise, factual, and cite which chunk your answer comes from when relevant."""

    user_message = f"""Context from uploaded documents:
{context_text}

---
User Question: {query}

Answer based on the context above:"""

    response = await _client().chat.completions.create(
        model=OPENAI_VISION_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        max_tokens=1500,
        temperature=0.3
    )

    return response.choices[0].message.content.strip()


async def answer_general(query: str) -> str:
    """
    Answer as a normal chat assistant when no indexed document context is available.
    """
    if client is None:
        return (
            "The backend is running, but the OpenAI API key is not configured yet. "
            "Please add OPENAI_API_KEY as a Hugging Face Space secret, then restart "
            "the Space. After that I can answer normally and process uploaded documents."
        )

    system_prompt = """You are a helpful AI assistant.
Answer the user's question directly and clearly.
If the question appears to be about uploaded documents, explain that no document context is currently available and answer generally if possible."""

    response = await _client().chat.completions.create(
        model=OPENAI_VISION_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
        max_tokens=1500,
        temperature=0.5,
    )

    return response.choices[0].message.content.strip()
