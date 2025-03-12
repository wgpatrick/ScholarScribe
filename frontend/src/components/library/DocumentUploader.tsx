import { useState, useRef, ChangeEvent, DragEvent } from 'react'

interface DocumentUploaderProps {
  onUpload: (file: File) => void
  isUploading?: boolean
}

const DocumentUploader = ({ onUpload, isUploading = false }: DocumentUploaderProps) => {
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  // Handle file selection
  const handleFileSelect = (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      onUpload(files[0])
    }
  }
  
  // Handle drag events
  const handleDragEnter = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }
  
  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }
  
  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }
  
  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
    
    const files = e.dataTransfer.files
    if (files && files.length > 0) {
      onUpload(files[0])
    }
  }
  
  // Trigger file input click
  const handleButtonClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click()
    }
  }
  
  return (
    <div
      className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
        isDragging ? 'bg-primary-50 border-primary-400' : 'border-gray-300 hover:border-primary-300'
      }`}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
    >
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileSelect}
        className="hidden"
        accept=".pdf"
        disabled={isUploading}
      />
      
      <div className="mb-4">
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          stroke="currentColor"
          fill="none"
          viewBox="0 0 48 48"
          aria-hidden="true"
        >
          <path
            d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
            strokeWidth={2}
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </div>
      
      <div className="text-center">
        <p className="text-lg font-semibold text-gray-900">
          {isUploading ? 'Uploading...' : 'Drag and drop your PDF file'}
        </p>
        <p className="mt-1 text-sm text-gray-500">
          {isUploading 
            ? 'Please wait while we process your document' 
            : 'Or click the button below to browse your files'}
        </p>
      </div>
      
      {!isUploading && (
        <button
          type="button"
          className="mt-4 btn btn-primary"
          onClick={handleButtonClick}
        >
          Browse Files
        </button>
      )}
      
      {isUploading && (
        <div className="mt-4 flex justify-center items-center">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-700"></div>
          <span className="ml-2 text-primary-700">Uploading...</span>
        </div>
      )}
    </div>
  )
}

export default DocumentUploader