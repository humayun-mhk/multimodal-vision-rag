import { useState, useEffect } from 'react'
import { Brain, Database, Zap, RotateCcw } from 'lucide-react'
import ChatBox from './components/ChatBox'
import UploadPanel from './components/UploadPanel'
import { getStats, resetIndex } from './services/api'

export default function App() {
  const [stats, setStats] = useState({ total_vectors: 0, sources: [] })
  const [notification, setNotification] = useState(null)

  const fetchStats = async () => {
    try {
      const s = await getStats()
      setStats(s)
    } catch (_) {}
  }

  useEffect(() => { fetchStats() }, [])

  const showNotification = (msg, type = 'success') => {
    setNotification({ msg, type })
    setTimeout(() => setNotification(null), 4000)
  }

  const handleUploadSuccess = (result) => {
    showNotification(`✓ ${result.filename} — ${result.chunks_added} chunks indexed`)
    fetchStats()
  }

  const handleReset = async () => {
    if (!confirm('Clear all indexed documents? This cannot be undone.')) return
    try {
      await resetIndex()
      setStats({ total_vectors: 0, sources: [] })
      showNotification('Index cleared', 'info')
    } catch (_) {
      showNotification('Failed to reset index', 'error')
    }
  }

  return (
    <div className="flex flex-col h-screen bg-gray-950 text-gray-100">
      {/* Top nav */}
      <header className="flex items-center justify-between px-6 py-3 border-b border-gray-800 bg-gray-950/80 backdrop-blur-sm z-10">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-sky-600 flex items-center justify-center">
            <Brain size={18} className="text-white" />
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-tight text-white">Multimodal RAG</h1>
            <p className="text-xs text-gray-500">GPT-4o · FAISS · FastAPI</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="hidden sm:flex items-center gap-1.5 text-xs text-gray-400">
            <Database size={12} className="text-sky-400" />
            <span>{stats.total_vectors} vectors</span>
          </div>
          <div className="hidden sm:flex items-center gap-1.5 text-xs text-gray-400">
            <Zap size={12} className="text-emerald-400" />
            <span>{stats.sources?.length || 0} documents</span>
          </div>
          {stats.total_vectors > 0 && (
            <button
              onClick={handleReset}
              className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-red-400 transition-colors"
            >
              <RotateCcw size={12} />
              <span className="hidden sm:inline">Reset</span>
            </button>
          )}
        </div>
      </header>

      {/* Notification */}
      {notification && (
        <div className={`mx-4 mt-3 px-4 py-2.5 rounded-lg text-xs font-medium animate-fade-in
          ${notification.type === 'error' ? 'bg-red-900/50 border border-red-700 text-red-300' :
            notification.type === 'info' ? 'bg-gray-800 border border-gray-700 text-gray-300' :
            'bg-emerald-900/50 border border-emerald-700 text-emerald-300'}`}>
          {notification.msg}
        </div>
      )}

      {/* Main layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left sidebar — upload */}
        <aside className="w-72 flex-shrink-0 border-r border-gray-800 bg-gray-900/50 flex flex-col">
          <div className="px-4 py-3 border-b border-gray-800">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
              Document Upload
            </h2>
          </div>
          <div className="flex-1 overflow-y-auto p-4">
            <UploadPanel onUploadSuccess={handleUploadSuccess} />

            {/* Source list */}
            {stats.sources?.length > 0 && (
              <div className="mt-6">
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
                  Indexed Files
                </p>
                <div className="space-y-1">
                  {stats.sources.map((src, i) => (
                    <div key={i} className="flex items-center gap-2 text-xs text-gray-400 py-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 flex-shrink-0" />
                      <span className="truncate font-mono">{src}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </aside>

        {/* Chat area */}
        <main className="flex-1 flex flex-col overflow-hidden">
          <ChatBox documentsIndexed={stats.total_vectors} />
        </main>
      </div>
    </div>
  )
}
