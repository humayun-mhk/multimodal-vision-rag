FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libmupdf-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

ENV PORT=7860
ENV FAISS_INDEX_PATH=/data/faiss_index

RUN mkdir -p /data/faiss_index && chmod 777 /data

EXPOSE 7860

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-7860}"]
