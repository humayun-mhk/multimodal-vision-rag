import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
})

/**
 * Upload a file (PDF, image, or text) to the RAG backend.
 * @param {File} file
 * @param {function} onProgress - optional progress callback (0-100)
 */
export async function uploadFile(file, onProgress) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (onProgress && e.total) {
        onProgress(Math.round((e.loaded / e.total) * 100))
      }
    }
  })

  return response.data
}

/**
 * Send a query to the RAG system and get an AI answer.
 * @param {string} query
 * @param {number} topK - number of chunks to retrieve
 */
export async function sendQuery(query, topK = 5) {
  const response = await api.post('/query', { query, top_k: topK })
  return response.data
}

/**
 * Get FAISS index statistics.
 */
export async function getStats() {
  const response = await api.get('/stats')
  return response.data
}

/**
 * Reset / clear the vector index.
 */
export async function resetIndex() {
  const response = await api.delete('/reset')
  return response.data
}
