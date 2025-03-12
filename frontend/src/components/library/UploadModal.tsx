import { Fragment, useState } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import DocumentUploader from './DocumentUploader'
import ProcessingStatus from './ProcessingStatus'
import { uploadDocument } from '../../api/documents'
import { useUI } from '../../context/UIContext'

interface UploadModalProps {
  isOpen: boolean
  onClose: () => void
  onUploadComplete: (documentId: string) => void
}

const UploadModal = ({ isOpen, onClose, onUploadComplete }: UploadModalProps) => {
  const [file, setFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [processingStatus, setProcessingStatus] = useState<'pending' | 'processing' | 'completed' | 'failed'>('pending')
  const [documentId, setDocumentId] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | undefined>(undefined)

  // Handle file selection
  const handleFileUpload = async (selectedFile: File) => {
    setFile(selectedFile)
    setIsUploading(true)
    setUploadProgress(10)
    
    try {
      // Simulated progress for now
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 10
        })
      }, 500)
      
      // In a real implementation, we would use uploadDocument from the API
      // const response = await uploadDocument(selectedFile)
      
      // For now, simulate a response
      await new Promise(resolve => setTimeout(resolve, 3000))
      const mockDocumentId = Date.now().toString()
      
      clearInterval(progressInterval)
      setUploadProgress(100)
      setDocumentId(mockDocumentId)
      setProcessingStatus('completed')
      
      // For production, use the commented code below
      // setDocumentId(response.id)
      // setProcessingStatus(response.processing_status)
      
    } catch (error) {
      console.error('Upload error:', error)
      setProcessingStatus('failed')
      setErrorMessage(error instanceof Error ? error.message : 'An unknown error occurred')
    } finally {
      setIsUploading(false)
    }
  }
  
  // Handle completion
  const handleComplete = () => {
    if (documentId) {
      onUploadComplete(documentId)
      onClose()
    }
  }
  
  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-10" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/25" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                <Dialog.Title
                  as="h3"
                  className="text-lg font-medium leading-6 text-gray-900"
                >
                  Upload Academic Paper
                </Dialog.Title>
                
                <div className="mt-4">
                  {!file ? (
                    <DocumentUploader 
                      onUpload={handleFileUpload} 
                      isUploading={isUploading} 
                    />
                  ) : (
                    <div className="space-y-4">
                      <div className="flex items-center space-x-4">
                        <svg className="w-8 h-8 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <div className="flex-1 truncate">
                          <p className="font-medium text-gray-900 truncate">{file.name}</p>
                          <p className="text-sm text-gray-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                        </div>
                      </div>
                      
                      <ProcessingStatus
                        status={processingStatus}
                        progress={uploadProgress}
                        errorMessage={errorMessage}
                        onComplete={handleComplete}
                      />
                    </div>
                  )}
                </div>

                <div className="mt-6 flex justify-end">
                  <button
                    type="button"
                    className="btn btn-secondary mr-2"
                    onClick={onClose}
                    disabled={isUploading}
                  >
                    Cancel
                  </button>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  )
}

export default UploadModal