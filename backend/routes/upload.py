from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from services.openai_service import extract_from_image
from services.vector_db import add_documents, get_index_stats
from utils.chunker import chunk_text, clean_text
from utils.pdf_parser import extract_text_from_pdf, pdf_to_images, is_scanned_pdf

router = APIRouter()

SUPPORTED_TYPES = {
    "application/pdf": "pdf",
    "image/jpeg": "image",
    "image/png": "image",
    "image/webp": "image",
    "image/gif": "image",
    "text/plain": "text",
}


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a PDF, image, or text file.
    Extracts content, chunks it, embeds it, and stores in FAISS.
    """
    content_type = file.content_type or ""
    file_type = SUPPORTED_TYPES.get(content_type)

    if not file_type:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {content_type}. Supported: PDF, JPEG, PNG, WebP, TXT"
        )

    file_bytes = await file.read()
    filename = file.filename or "upload"
    extracted_text = ""
    extraction_meta = {}

    try:
        if file_type == "text":
            raw = file_bytes.decode("utf-8", errors="replace")
            extracted_text = clean_text(raw)
            extraction_meta = {"method": "direct_text"}

        elif file_type == "image":
            result = await extract_from_image(file_bytes, filename)
            extracted_text = clean_text(result.get("text", ""))
            extraction_meta = {
                "method": "gpt4o_vision",
                "summary": result.get("summary", ""),
                "entities": result.get("entities", [])
            }

        elif file_type == "pdf":
            if is_scanned_pdf(file_bytes):
                # Scanned PDF — convert pages to images and use GPT-4o Vision
                images = pdf_to_images(file_bytes)
                all_text = []
                for i, img_bytes in enumerate(images):
                    result = await extract_from_image(img_bytes, f"{filename}_page{i+1}")
                    page_text = result.get("text", "")
                    if page_text.strip():
                        all_text.append(f"[Page {i+1}]\n{page_text}")
                extracted_text = clean_text("\n\n".join(all_text))
                extraction_meta = {"method": "gpt4o_vision_pdf"}
            else:
                raw = extract_text_from_pdf(file_bytes)
                extracted_text = clean_text(raw)
                extraction_meta = {"method": "pymupdf_text"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

    if not extracted_text:
        raise HTTPException(status_code=422, detail="No content could be extracted from this file.")

    # Chunk and index
    chunks = chunk_text(extracted_text)
    if not chunks:
        raise HTTPException(status_code=422, detail="Text extraction produced no usable chunks.")

    await add_documents(chunks, source=filename)
    stats = get_index_stats()

    return JSONResponse({
        "status": "success",
        "filename": filename,
        "file_type": file_type,
        "extraction_method": extraction_meta.get("method"),
        "chunks_added": len(chunks),
        "total_vectors": stats["total_vectors"],
        "preview": extracted_text[:300] + ("..." if len(extracted_text) > 300 else ""),
        **({k: v for k, v in extraction_meta.items() if k != "method"})
    })


@router.get("/stats")
def index_stats():
    """Return current FAISS index statistics."""
    return get_index_stats()


@router.delete("/reset")
def reset_index_route():
    """Clear the vector index (start fresh)."""
    from services.vector_db import reset_index
    reset_index()
    return {"status": "index cleared"}
