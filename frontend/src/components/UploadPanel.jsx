import { useState, useRef } from 'react'
import { Upload, FileText, Image, File, X, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import { uploadFile } from '../services/api'

const ACCEPTED_TYPES = {
  'application/pdf': { icon: FileText, label: 'PDF', color: 'text-red-400' },
  'image/jpeg': { icon: Image, label: 'JPEG', color: 'text-blue-400' },
  'image/png': { icon: Image, label: 'PNG', color: 'text-blue-400' },
  'image/webp': { icon: Image, label: 'WebP', color: 'text-blue-400' },
  'text/plain': { icon: FileText, label: 'TXT', color: 'text-green-400' },
}

function FileItem({ file, status, progress, error, onRemove }) {
  const typeInfo = ACCEPTED_TYPES[file.type] || { icon: File, label: 'File', color: 'text-gray-400' }
  const Icon = typeInfo.icon

  return (
    <div className="flex items-center gap-3 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2.5">
      <Icon size={16} className={typeInfo.color} />
      <div className="flex-1 min-w-0">
        <p className="text-xs font-medium text-gray-200 truncate">{file.name}</p>
        <p className="text-xs text-gray-500">
          {(file.size / 1024).toFixed(1)} KB
        </p>
      </div>

      <div className="flex items-center gap-2 flex-shrink-0">
        {status === 'uploading' && (
          <>
            <span className="text-xs text-sky-400">{progress}%</span>
            <Loader2 size={14} className="text-sky-400 animate-spin" />
          </>
        )}
        {status === 'success' && <CheckCircle size={16} className="text-emerald-400" />}
        {status === 'error' && (
          <div className="flex items-center gap-1">
            <AlertCircle size={14} className="text-red-400" />
            <span className="text-xs text-red-400 max-w-[100px] truncate">{error}</span>
          </div>
        )}
        {status === 'idle' && (
          <button onClick={() => onRemove(file)} className="text-gray-500 hover:text-gray-300">
            <X size={14} />
          </button>
        )}
      </div>
    </div>
  )
}

export default function UploadPanel({ onUploadSuccess }) {
  const [files, setFiles] = useState([])
  const [fileStates, setFileStates] = useState({})
  const [isDragging, setIsDragging] = useState(false)
  const inputRef = useRef(null)

  const addFiles = (newFiles) => {
    const validFiles = Array.from(newFiles).filter(f => ACCEPTED_TYPES[f.type])
    setFiles(prev => {
      const names = new Set(prev.map(f => f.name))
      return [...prev, ...validFiles.filter(f => !names.has(f.name))]
    })
  }

  const removeFile = (file) => {
    setFiles(prev => prev.filter(f => f.name !== file.name))
    setFileStates(prev => { const s = { ...prev }; delete s[file.name]; return s })
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    addFiles(e.dataTransfer.files)
  }

  const uploadAll = async () => {
    const pending = files.filter(f => !fileStates[f.name] || fileStates[f.name].status === 'error')
    if (!pending.length) return

    for (const file of pending) {
      setFileStates(prev => ({ ...prev, [file.name]: { status: 'uploading', progress: 0 } }))
      try {
        const result = await uploadFile(file, (pct) => {
          setFileStates(prev => ({ ...prev, [file.name]: { status: 'uploading', progress: pct } }))
        })
        setFileStates(prev => ({ ...prev, [file.name]: { status: 'success' } }))
        if (onUploadSuccess) onUploadSuccess(result)
      } catch (err) {
        const msg = err.response?.data?.detail || 'Upload failed'
        setFileStates(prev => ({ ...prev, [file.name]: { status: 'error', error: msg } }))
      }
    }
  }

  const hasReady = files.some(f => !fileStates[f.name] || fileStates[f.name].status === 'error')

  return (
    <div className="space-y-3">
      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`
          border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all duration-200
          ${isDragging
            ? 'border-sky-500 bg-sky-500/10'
            : 'border-gray-600 hover:border-gray-500 hover:bg-gray-800/50'}
        `}
      >
        <Upload size={24} className="mx-auto mb-2 text-gray-400" />
        <p className="text-sm font-medium text-gray-300">Drop files here</p>
        <p className="text-xs text-gray-500 mt-1">PDF, PNG, JPEG, WebP, TXT</p>
        <input
          ref={inputRef}
          type="file"
          multiple
          accept=".pdf,.jpg,.jpeg,.png,.webp,.txt"
          className="hidden"
          onChange={(e) => addFiles(e.target.files)}
        />
      </div>

      {/* File list */}
      {files.length > 0 && (
        <div className="space-y-2">
          {files.map(file => (
            <FileItem
              key={file.name}
              file={file}
              status={fileStates[file.name]?.status || 'idle'}
              progress={fileStates[file.name]?.progress || 0}
              error={fileStates[file.name]?.error}
              onRemove={removeFile}
            />
          ))}

          <button
            onClick={uploadAll}
            disabled={!hasReady}
            className="w-full py-2 px-4 bg-sky-600 hover:bg-sky-500 disabled:bg-gray-700 disabled:text-gray-500 text-white text-sm font-medium rounded-lg transition-colors"
          >
            Upload {hasReady ? 'Files' : '(all done)'}
          </button>
        </div>
      )}
    </div>
  )
}
