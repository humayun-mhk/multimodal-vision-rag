from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import upload, query
import uvicorn

app = FastAPI(
    title="Multimodal RAG API",
    description="RAG system supporting PDF, image, and text with GPT-4o",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set your frontend URL
    allow_credentials=True,
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
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
