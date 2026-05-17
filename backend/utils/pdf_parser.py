import io
import fitz  # PyMuPDF
from PIL import Image


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract all text from a PDF file using PyMuPDF."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        if text.strip():
            full_text.append(f"[Page {page_num + 1}]\n{text}")

    doc.close()
    return "\n\n".join(full_text)


def pdf_to_images(pdf_bytes: bytes, dpi: int = 150) -> list[bytes]:
    """
    Convert each PDF page to a JPEG image (bytes).
    Used when PDF has no selectable text (scanned).
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []
    mat = fitz.Matrix(dpi / 72, dpi / 72)

    for page in doc:
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        images.append(buf.getvalue())

    doc.close()
    return images


def is_scanned_pdf(pdf_bytes: bytes, text_threshold: int = 50) -> bool:
    """Detect if a PDF is likely scanned (minimal extractable text)."""
    text = extract_text_from_pdf(pdf_bytes)
    return len(text.strip()) < text_threshold
