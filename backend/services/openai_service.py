import json
from google.genai import types

from config import GEMINI_MODEL
from services.gemini_client import get_gemini_client, is_gemini_configured
from utils.chat import plain_text


def _client():
    return get_gemini_client()


async def extract_from_image(image_bytes: bytes, filename: str = "image") -> dict:
    """
    Use Gemini vision to extract structured content from an image.
    Returns: { text, summary, entities }
    """
    system_prompt = """You are an expert document and image analyzer.
Extract all readable text and meaningful information from the provided image.
Respond ONLY with valid JSON in this exact format:
{
  "text": "full extracted text from image",
  "summary": "concise 2-3 sentence summary of content",
  "entities": ["list", "of", "key", "entities", "found"]
}"""

    response = await _client().aio.models.generate_content(
        model=GEMINI_MODEL,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            f"Extract all content from this image (filename: {filename}). Return valid JSON only.",
        ],
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=2000,
            temperature=0.1,
            response_mime_type="application/json",
        ),
    )

    raw = (response.text or "").strip()

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
    Send user query and retrieved context to Gemini for a final answer.
    """
    context_text = "\n\n---\n\n".join(
        [f"[Chunk {i+1}]:\n{chunk}" for i, chunk in enumerate(context_chunks)]
    )

    system_prompt = """You are a helpful AI assistant with access to documents uploaded by the user.
Use the provided context chunks to answer the question accurately.
If the answer is not found in the context, say so clearly.
Be concise, factual, and cite which chunk your answer comes from when relevant.
Do not use Markdown bold markers or asterisks in the answer."""

    user_message = f"""Context from uploaded documents:
{context_text}

---
User Question: {query}

Answer based on the context above:"""

    response = await _client().aio.models.generate_content(
        model=GEMINI_MODEL,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=1500,
            temperature=0.3,
        ),
    )

    return plain_text(response.text)


async def answer_general(query: str) -> str:
    """
    Answer as a normal chat assistant when no indexed document context is available.
    """
    if not is_gemini_configured():
        return (
            "The backend is running, but the Google API key is not configured yet. "
            "Please add GOOGLE_API_KEY as a Hugging Face Space secret, then restart "
            "the Space. After that I can answer normally and process uploaded documents."
        )

    system_prompt = """You are a helpful AI assistant.
Answer the user's question directly and clearly.
If the question appears to be about uploaded documents, explain that no document context is currently available and answer generally if possible.
Do not use Markdown bold markers or asterisks in the answer."""

    response = await _client().aio.models.generate_content(
        model=GEMINI_MODEL,
        contents=query,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=1500,
            temperature=0.5,
        ),
    )

    return plain_text(response.text)
