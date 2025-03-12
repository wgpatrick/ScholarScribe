import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import UploadModal from '../components/library/UploadModal'
import { useLibrary } from '../context/LibraryContext'
import { useUI } from '../context/UIContext'

const LibraryDashboard = () => {
  const { 
    documents, 
    isLoading, 
    error, 
    refreshDocuments, 
    searchQuery, 
    setSearchQuery, 
    filteredDocuments,
    viewMode,
    setViewMode
  } = useLibrary();
  
  const { 
    isUploadModalOpen, 
    setUploadModalOpen,
    showToast 
  } = useUI();
  
  const navigate = useNavigate();
  
  // Handle document upload completion
  const handleUploadComplete = (documentId: string) => {
    refreshDocuments();
    showToast('Document uploaded successfully!', 'success');
    navigate(`/documents/${documentId}`);
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Your Library</h1>
      </div>
      
      {/* Upload Modal */}
      <UploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
        onUploadComplete={handleUploadComplete}
      />

      {/* Search and filters */}
      <div className="mb-6">
        <div className="flex gap-4">
          <div className="flex-grow">
            <input
              type="text"
              placeholder="Search papers..."
              className="input w-full"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <div className="flex gap-2">
            <button 
              className={`btn ${viewMode === 'grid' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setViewMode('grid')}
            >
              Grid
            </button>
            <button 
              className={`btn ${viewMode === 'list' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setViewMode('list')}
            >
              List
            </button>
          </div>
        </div>
      </div>
      
      {/* Loading and Error states */}
      {isLoading && (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-700 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading documents...</p>
        </div>
      )}
      
      {error && (
        <div className="text-center py-8">
          <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded-md">
            <p>{error}</p>
            <button 
              className="mt-4 btn btn-primary"
              onClick={refreshDocuments}
            >
              Try Again
            </button>
          </div>
        </div>
      )}

      {/* Document grid */}
      {viewMode === 'grid' ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredDocuments.map(doc => (
            <Link to={`/documents/${doc.id}`} key={doc.id} className="card p-6 hover:shadow-md transition-shadow duration-200">
              <h2 className="text-xl font-semibold">{doc.title}</h2>
              <p className="text-sm text-gray-600 mb-2">{doc.authors.join(', ')}</p>
              <p className="text-sm text-gray-700 mb-4 line-clamp-3">{doc.abstract}</p>
              <div className="flex justify-between items-center text-xs text-gray-500">
                <span>
                  {doc.status === 'processing' ? (
                    <span className="flex items-center">
                      <span className="animate-pulse mr-1 w-2 h-2 bg-accent-500 rounded-full"></span>
                      Processing
                    </span>
                  ) : (
                    <span>Ready to read</span>
                  )}
                </span>
                <span>
                  {doc.lastViewed ? (
                    `Last viewed: ${new Date(doc.lastViewed).toLocaleDateString()}`
                  ) : 'New'}
                </span>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {filteredDocuments.map(doc => (
            <Link to={`/documents/${doc.id}`} key={doc.id} className="card p-4 flex hover:shadow-md transition-shadow duration-200">
              <div className="flex-grow">
                <h2 className="text-lg font-semibold">{doc.title}</h2>
                <p className="text-sm text-gray-600">{doc.authors.join(', ')}</p>
              </div>
              <div className="flex flex-col justify-between items-end text-xs text-gray-500">
                <span>
                  {doc.status === 'processing' ? (
                    <span className="flex items-center">
                      <span className="animate-pulse mr-1 w-2 h-2 bg-accent-500 rounded-full"></span>
                      Processing
                    </span>
                  ) : (
                    <span>Ready to read</span>
                  )}
                </span>
                <span>
                  {doc.lastViewed ? (
                    `Last viewed: ${new Date(doc.lastViewed).toLocaleDateString()}`
                  ) : 'New'}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* Empty state */}
      {filteredDocuments.length === 0 && (
        <div className="text-center py-12">
          <h3 className="text-lg font-medium text-gray-900 mb-2">No papers found</h3>
          <p className="text-gray-600">Try adjusting your search or upload a new paper.</p>
        </div>
      )}
    </div>
  )
}

export default LibraryDashboard