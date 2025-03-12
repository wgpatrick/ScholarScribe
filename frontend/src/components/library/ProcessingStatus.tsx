import { useEffect, useState } from 'react'

interface ProcessingStatusProps {
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress?: number
  errorMessage?: string
  onComplete?: () => void
}

const ProcessingStatus = ({ 
  status, 
  progress = 0, 
  errorMessage,
  onComplete 
}: ProcessingStatusProps) => {
  const [displayProgress, setDisplayProgress] = useState(progress)
  
  // Smoothly animate progress
  useEffect(() => {
    if (progress > displayProgress) {
      const timer = setTimeout(() => {
        setDisplayProgress(prev => Math.min(prev + 1, progress))
      }, 50)
      
      return () => clearTimeout(timer)
    }
  }, [progress, displayProgress])
  
  // Call onComplete when status becomes completed
  useEffect(() => {
    if (status === 'completed' && onComplete) {
      onComplete()
    }
  }, [status, onComplete])
  
  // Get status-specific content
  const getStatusContent = () => {
    switch (status) {
      case 'pending':
        return {
          title: 'Preparing Document',
          description: 'Your document is in the queue for processing.',
          icon: (
            <svg className="w-6 h-6 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          )
        }
        
      case 'processing':
        return {
          title: 'Processing Document',
          description: 'We\'re analyzing and extracting content from your PDF.',
          icon: (
            <svg className="w-6 h-6 text-primary-500 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          )
        }
        
      case 'completed':
        return {
          title: 'Processing Complete',
          description: 'Your document is ready to view.',
          icon: (
            <svg className="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          )
        }
        
      case 'failed':
        return {
          title: 'Processing Failed',
          description: errorMessage || 'There was an error processing your document.',
          icon: (
            <svg className="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          )
        }
        
      default:
        return {
          title: 'Unknown Status',
          description: 'The document status is unknown.',
          icon: (
            <svg className="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          )
        }
    }
  }
  
  const { title, description, icon } = getStatusContent()
  
  return (
    <div className="border rounded-lg p-4 bg-white shadow-sm">
      <div className="flex items-center">
        <div className="flex-shrink-0">
          {icon}
        </div>
        <div className="ml-3">
          <h3 className="text-lg font-medium text-gray-900">{title}</h3>
          <p className="text-sm text-gray-500">{description}</p>
        </div>
      </div>
      
      {(status === 'pending' || status === 'processing') && (
        <div className="mt-4">
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div 
              className="bg-primary-600 h-2.5 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${displayProgress}%` }}
            ></div>
          </div>
          <div className="mt-1 text-xs text-gray-500 text-right">
            {displayProgress}% complete
          </div>
        </div>
      )}
      
      {status === 'completed' && (
        <div className="mt-4">
          <button
            type="button"
            className="btn btn-primary"
            onClick={onComplete}
          >
            View Document
          </button>
        </div>
      )}
      
      {status === 'failed' && (
        <div className="mt-4">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => window.location.reload()}
          >
            Try Again
          </button>
        </div>
      )}
    </div>
  )
}

export default ProcessingStatus