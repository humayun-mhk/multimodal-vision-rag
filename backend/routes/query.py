from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.vector_db import search, get_index_stats
from services.openai_service import answer_with_context
from config import TOP_K

router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    top_k: int = TOP_K


class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]
    chunks_used: int


@router.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """
    RAG query endpoint.
    Flow: query → embed → FAISS search → context → GPT-4o → answer
    """
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    stats = get_index_stats()
    if stats["total_vectors"] == 0:
        raise HTTPException(
            status_code=404,
            detail="No documents indexed yet. Please upload files first."
        )

    # Semantic search
    results = await search(query, top_k=request.top_k)
    if not results:
        raise HTTPException(status_code=404, detail="No relevant chunks found.")

    # Extract text chunks for context
    context_chunks = [r["text"] for r in results]

    # GPT-4o reasoning
    answer = await answer_with_context(query, context_chunks)

    # Format sources for response
    sources = [
        {"source": r["source"], "score": round(r["score"], 4), "preview": r["text"][:150]}
        for r in results
    ]

    return QueryResponse(
        answer=answer,
        sources=sources,
        chunks_used=len(context_chunks)
    )
