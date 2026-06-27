import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import upload, query
from config import CORS_ORIGINS, PORT
from services.openai_client import is_openai_configured
from services.vector_db import ensure_index_dir, load_index
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_index_dir()
    load_index()
    yield


app = FastAPI(
    title="Multimodal RAG API",
    description="RAG system supporting PDF, image, and text with GPT-4o",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials="*" not in CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(query.router, prefix="/api", tags=["Query"])

@app.get("/")
def root():
    return {"message": "Multimodal RAG API is running"}

@app.get("/health")
def health():
    return {"status": "ok", "openai_configured": is_openai_configured()}

@app.get("/api/health")
def api_health():
    return {"status": "ok", "openai_configured": is_openai_configured()}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        reload=os.getenv("ENVIRONMENT") == "development",
    )
