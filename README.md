---
title: Multimodal Vision RAG API
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# Multimodal RAG System

A production-ready Retrieval-Augmented Generation (RAG) system supporting **PDF, images, and text** powered by **GPT-4o**, **FAISS**, **FastAPI**, and **React**.

**Live Demo:** https://multimodal-vision-rag-dfqh.vercel.app/

---

## 🏗 Architecture

```
User uploads file (PDF / Image / Text)
         ↓
  FastAPI Backend receives file
         ↓
  GPT-4o Vision extracts content
         ↓
  Text chunked into segments
         ↓
  OpenAI Embeddings → FAISS index
         ↓
  User asks a question
         ↓
  Query embedded → FAISS semantic search
         ↓
  Top-K chunks retrieved as context
         ↓
  GPT-4o generates answer
         ↓
  React UI displays response + sources
```

---

## 📁 Project Structure

```
multimodal-rag/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Environment variables
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── routes/
│   │   ├── upload.py            # POST /api/upload
│   │   └── query.py             # POST /api/query
│   ├── services/
│   │   ├── openai_service.py    # GPT-4o vision + RAG answering
│   │   ├── embeddings_service.py # OpenAI embeddings
│   │   └── vector_db.py         # FAISS index management
│   └── utils/
│       ├── chunker.py           # Text splitting
│       └── pdf_parser.py        # PDF → text / images
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Main layout
│   │   ├── components/
│   │   │   ├── ChatBox.jsx      # Chat interface
│   │   │   ├── MessageBubble.jsx
│   │   │   └── UploadPanel.jsx  # File upload UI
│   │   └── services/
│   │       └── api.js           # Axios API calls
│   ├── Dockerfile
│   └── package.json
└── docker-compose.yml
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API key

### 1. Backend Setup

```bash
cd backend
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

pip install -r requirements.txt
python main.py
# API runs at http://localhost:8000
```

### 2. Frontend Setup

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
# UI runs at http://localhost:3000
```

---

## 🐳 Docker (Full Stack)

```bash
cp backend/.env.example .env
# Set OPENAI_API_KEY in .env

docker-compose up --build
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

---

## 📡 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/upload` | Upload a file for indexing |
| POST | `/api/query` | Query the RAG system |
| GET | `/api/stats` | Get FAISS index stats |
| DELETE | `/api/reset` | Clear all indexed data |

### Upload example
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@document.pdf"
```

### Query example
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main topic?", "top_k": 5}'
```

---

## ☁️ Deployment

### Backend → Render / Railway
1. Push `backend/` to a GitHub repo
2. Set `OPENAI_API_KEY` as an environment variable
3. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Frontend → Vercel
1. Push `frontend/` to GitHub
2. Set `VITE_API_URL` to your backend URL in Vercel env vars
3. Deploy with `npm run build` / output dir `dist`

---

## 🛠 Technologies

| Layer | Tech |
|-------|------|
| LLM | OpenAI GPT-4o |
| Embeddings | OpenAI text-embedding-3-small |
| Vector DB | FAISS (CPU) |
| Backend | FastAPI + Python 3.11 |
| PDF parsing | PyMuPDF |
| Frontend | React 18 + Vite |
| Styling | Tailwind CSS |
| HTTP | Axios |
| Deploy | Docker / Vercel / Render |

---

## Clean Deployment Path

### Backend on Hugging Face Spaces

Use a Docker Space from the repo root. The root `Dockerfile` builds the FastAPI backend and listens on port `7860`, matching the Space metadata at the top of this README.

Set these Hugging Face Space secrets or variables:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_VISION_MODEL=gpt-4o
FAISS_INDEX_PATH=/data/faiss_index
PORT=7860
CORS_ORIGINS=https://your-vercel-domain.vercel.app
```

Enable persistent storage on the Space if you want uploaded documents and FAISS index files to survive restarts. Without persistent storage, the app still works, but the index resets when the container restarts.

### Frontend on Vercel

Deploy the repo to Vercel. The root `vercel.json` builds the `frontend` folder.

Set these Vercel environment variables:

```env
VITE_API_URL=https://your-huggingface-space.hf.space/api
VITE_API_TIMEOUT_MS=180000
```

Build command: `npm run build --prefix frontend`
Output directory: `frontend/dist`

### Local URLs

Backend: `http://localhost:8000`
Frontend: `http://localhost:3000`
