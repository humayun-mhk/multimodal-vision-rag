import os
import json
import numpy as np
import faiss
from config import FAISS_INDEX_PATH
from services.embeddings_service import get_embeddings_batch, get_embedding_dimension

# In-memory store for document chunks metadata
_metadata: list[dict] = []
_index: faiss.IndexFlatL2 | None = None

INDEX_FILE = os.path.join(FAISS_INDEX_PATH, "index.bin")
META_FILE = os.path.join(FAISS_INDEX_PATH, "metadata.json")


def _get_or_create_index() -> faiss.IndexFlatL2:
    global _index
    if _index is None:
        dim = get_embedding_dimension()
        _index = faiss.IndexFlatL2(dim)
    return _index


def save_index():
    """Persist FAISS index and metadata to disk."""
    idx = _get_or_create_index()
    faiss.write_index(idx, INDEX_FILE)
    with open(META_FILE, "w") as f:
        json.dump(_metadata, f, indent=2)


def load_index():
    """Load FAISS index and metadata from disk if available."""
    global _index, _metadata
    if os.path.exists(INDEX_FILE) and os.path.exists(META_FILE):
        _index = faiss.read_index(INDEX_FILE)
        with open(META_FILE, "r") as f:
            _metadata = json.load(f)
        print(f"[FAISS] Loaded index with {_index.ntotal} vectors")
    else:
        _index = None
        _metadata = []


def reset_index():
    """Clear the FAISS index (for fresh uploads)."""
    global _index, _metadata
    dim = get_embedding_dimension()
    _index = faiss.IndexFlatL2(dim)
    _metadata = []


async def add_documents(chunks: list[str], source: str = "unknown"):
    """
    Embed a list of text chunks and add them to the FAISS index.
    """
    global _metadata

    if not chunks:
        return

    embeddings = await get_embeddings_batch(chunks)
    vectors = np.array(embeddings, dtype="float32")

    idx = _get_or_create_index()
    idx.add(vectors)

    for i, chunk in enumerate(chunks):
        _metadata.append({
            "source": source,
            "chunk_index": i,
            "text": chunk
        })

    save_index()
    print(f"[FAISS] Added {len(chunks)} chunks from '{source}'. Total: {idx.ntotal}")


async def search(query_text: str, top_k: int = 5) -> list[dict]:
    """
    Search the FAISS index for the most relevant chunks.
    Returns list of {text, source, score} dicts.
    """
    from services.embeddings_service import get_embedding

    idx = _get_or_create_index()

    if idx.ntotal == 0:
        return []

    query_vec = await get_embedding(query_text)
    query_arr = np.array([query_vec], dtype="float32")

    k = min(top_k, idx.ntotal)
    distances, indices = idx.search(query_arr, k)

    results = []
    for dist, i in zip(distances[0], indices[0]):
        if i == -1:
            continue
        meta = _metadata[i]
        results.append({
            "text": meta["text"],
            "source": meta["source"],
            "score": float(dist)
        })

    return results


def get_index_stats() -> dict:
    idx = _get_or_create_index()
    return {
        "total_vectors": idx.ntotal,
        "total_chunks": len(_metadata),
        "sources": list(set(m["source"] for m in _metadata))
    }
